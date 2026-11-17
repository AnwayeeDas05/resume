import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from app.models import ResumeParsedModel, BatchUploadResponse
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.resume_extractor import parse_resume_content
from app.database import db_manager

logger = logging.getLogger("resume_matcher.resume_routes")

router = APIRouter(prefix="/resumes", tags=["Resumes"])

async def upsert_candidate(db, parsed_candidate: ResumeParsedModel) -> str:
    """
    Inserts a candidate or updates if a resume with the same filename or email exists.
    Prevents duplicates in candidate pool.
    """
    existing = await db["resumes"].find_one({
        "$or": [
            {"filename": parsed_candidate.filename},
            {"email": parsed_candidate.email} if parsed_candidate.email else {"filename": parsed_candidate.filename}
        ]
    })
    if existing:
        cand_id = existing["id"]
        parsed_candidate.id = cand_id
        await db["resumes"].update_one(
            {"id": cand_id},
            {"$set": parsed_candidate.model_dump()}
        )
        return cand_id
    else:
        await db["resumes"].insert_one(parsed_candidate.model_dump())
        return parsed_candidate.id

@router.post("/upload", response_model=BatchUploadResponse)
async def upload_resumes_batch(files: List[UploadFile] = File(...)):
    """
    Handles batch upload of resumes (PDF, DOCX, TXT).
    Processes files individually so an invalid or corrupt file does NOT interrupt
    the batch. Replaces/upserts existing files with matching filenames to prevent duplicates.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    successful_candidates: List[ResumeParsedModel] = []
    failed_files: List[Dict[str, str]] = []
    db = db_manager.get_db()

    for file in files:
        filename = file.filename or "unknown_resume"
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        
        try:
            content_bytes = await file.read()
            if not content_bytes or len(content_bytes) < 10:
                failed_files.append({"filename": filename, "reason": "Empty or zero-byte file"})
                continue

            # Extract raw text depending on extension
            if ext == "pdf":
                raw_text, _ = extract_text_from_pdf(content_bytes, filename)
            elif ext in ["docx", "doc"]:
                raw_text, _ = extract_text_from_docx(content_bytes, filename)
            elif ext in ["txt", "md"]:
                raw_text = content_bytes.decode("utf-8", errors="ignore")
            else:
                failed_files.append({
                    "filename": filename,
                    "reason": f"Unsupported format (.{ext}). Supported formats: .pdf, .docx, .txt"
                })
                continue

            candidate_id = f"cand_{uuid.uuid4().hex[:10]}"
            parsed_candidate = parse_resume_content(
                raw_text=raw_text,
                filename=filename,
                candidate_id=candidate_id
            )

            # Upsert into DB to prevent duplicate entries
            await upsert_candidate(db, parsed_candidate)
            successful_candidates.append(parsed_candidate)

        except Exception as e:
            logger.warning(f"Failed to process resume '{filename}': {str(e)}")
            failed_files.append({
                "filename": filename,
                "reason": str(e)
            })

    return BatchUploadResponse(
        total_uploaded=len(files),
        successful_count=len(successful_candidates),
        failed_count=len(failed_files),
        successful_candidates=successful_candidates,
        failed_files=failed_files
    )

@router.post("/load-samples", response_model=BatchUploadResponse)
async def load_sample_resumes(include_corrupted: bool = Query(False, description="Whether to include corrupted test file")):
    """
    Loads all valid sample resumes from sample_resumes directory.
    By default, only loads the 11 valid candidate resumes without false-alarm error warnings.
    Upserts each candidate so multiple clicks do not create duplicate records.
    """
    from app.config import settings
    sample_files = list(settings.SAMPLES_DIR.glob("*.*"))
    
    # Filter only resumes (exclude JDs)
    resume_files = [
        f for f in sample_files 
        if not f.name.startswith("Sample_JD_") and f.suffix.lower() in [".pdf", ".docx", ".txt"]
    ]

    # If include_corrupted is False, exclude files named 'corrupted' or 'invalid'
    if not include_corrupted:
        resume_files = [f for f in resume_files if "corrupt" not in f.name.lower() and "invalid" not in f.name.lower()]

    if not resume_files:
        raise HTTPException(status_code=404, detail="No sample resume files found in sample_resumes folder.")

    successful_candidates: List[ResumeParsedModel] = []
    failed_files: List[Dict[str, str]] = []
    db = db_manager.get_db()

    for path in sorted(resume_files):
        filename = path.name
        ext = path.suffix.lower().lstrip(".")
        try:
            with open(path, "rb") as f:
                content_bytes = f.read()

            if ext == "pdf":
                raw_text, _ = extract_text_from_pdf(content_bytes, filename)
            elif ext in ["docx", "doc"]:
                raw_text, _ = extract_text_from_docx(content_bytes, filename)
            elif ext in ["txt", "md"]:
                raw_text = content_bytes.decode("utf-8", errors="ignore")
            else:
                failed_files.append({"filename": filename, "reason": f"Unsupported format: {ext}"})
                continue

            candidate_id = f"cand_{uuid.uuid4().hex[:10]}"
            parsed = parse_resume_content(raw_text, filename, candidate_id)
            
            # Upsert into DB to guarantee deduplication
            await upsert_candidate(db, parsed)
            successful_candidates.append(parsed)
        except Exception as e:
            failed_files.append({"filename": filename, "reason": str(e)})

    return BatchUploadResponse(
        total_uploaded=len(resume_files),
        successful_count=len(successful_candidates),
        failed_count=len(failed_files),
        successful_candidates=successful_candidates,
        failed_files=failed_files
    )

@router.post("/test-corrupted-upload", response_model=BatchUploadResponse)
async def test_corrupted_upload():
    """
    Explicit endpoint to test batch resilience by processing a corrupted PDF
    along with a valid resume, verifying that invalid files do not break the batch.
    """
    return await load_sample_resumes(include_corrupted=True)

@router.get("", response_model=List[ResumeParsedModel])
async def list_resumes():
    """Returns all parsed candidate resumes, deduplicated by filename/email."""
    db = db_manager.get_db()
    cursor = db["resumes"].find().sort("created_at", -1)
    results = await cursor.to_list(500)
    
    # In-memory deduplication pass in case prior duplicates exist in the collection
    seen_keys = set()
    deduped = []
    for doc in results:
        key = doc.get("filename") or doc.get("email") or doc.get("name")
        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(ResumeParsedModel(**doc))

    return deduped

@router.get("/{candidate_id}", response_model=ResumeParsedModel)
async def get_resume(candidate_id: str):
    """Retrieves an individual parsed resume by candidate ID."""
    db = db_manager.get_db()
    doc = await db["resumes"].find_one({"id": candidate_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate resume not found")
    return ResumeParsedModel(**doc)

@router.delete("/clear")
async def clear_resumes():
    """Clears all stored resumes and matching runs."""
    db = db_manager.get_db()
    try:
        docs = await db["resumes"].find().to_list(1000)
        for d in docs:
            await db["resumes"].delete_one({"id": d["id"]})
    except Exception as e:
        logger.warning(f"Clear collection note: {e}")

    return {"message": "Candidate pool cleared successfully"}
