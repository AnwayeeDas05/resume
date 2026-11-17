import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from app.models import JobDescriptionInput, JobDescriptionModel, WeightsConfig
from app.parsers.jd_extractor import extract_jd_entities
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.database import db_manager

router = APIRouter(prefix="/jd", tags=["Job Description"])

@router.post("", response_model=JobDescriptionModel)
async def create_job_description(payload: JobDescriptionInput):
    """
    Creates and analyzes a Job Description from raw text input.
    Extracts required/preferred skills, required experience, education, responsibilities.
    """
    jd_id = f"jd_{uuid.uuid4().hex[:10]}"
    jd = extract_jd_entities(
        text=payload.text,
        title=payload.title,
        company=payload.company or "Organization",
        jd_id=jd_id,
        weights=payload.weights
    )

    db = db_manager.get_db()
    await db["job_descriptions"].insert_one(jd.model_dump())
    return jd

@router.post("/upload", response_model=JobDescriptionModel)
async def upload_job_description_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    company: Optional[str] = Form("Organization")
):
    """
    Uploads a JD file (PDF, DOCX, or TXT), extracts requirements and stores in DB.
    """
    filename = file.filename or "job_description.txt"
    ext = filename.split(".")[-1].lower()
    content_bytes = await file.read()

    try:
        if ext == "pdf":
            raw_text, _ = extract_text_from_pdf(content_bytes, filename)
        elif ext in ["docx", "doc"]:
            raw_text, _ = extract_text_from_docx(content_bytes, filename)
        elif ext in ["txt", "md"]:
            raw_text = content_bytes.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format .{ext}. Please upload PDF, DOCX, or TXT.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse JD file: {str(e)}")

    derived_title = title or filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title()
    jd_id = f"jd_{uuid.uuid4().hex[:10]}"

    jd = extract_jd_entities(
        text=raw_text,
        title=derived_title,
        company=company or "Organization",
        jd_id=jd_id
    )

    db = db_manager.get_db()
    await db["job_descriptions"].insert_one(jd.model_dump())
    return jd

@router.get("", response_model=List[JobDescriptionModel])
async def list_job_descriptions():
    """Returns all stored Job Descriptions."""
    db = db_manager.get_db()
    cursor = db["job_descriptions"].find().sort("created_at", -1)
    results = await cursor.to_list(100)
    return [JobDescriptionModel(**doc) for doc in results]

@router.get("/{jd_id}", response_model=JobDescriptionModel)
async def get_job_description(jd_id: str):
    """Retrieves a single Job Description by ID."""
    db = db_manager.get_db()
    doc = await db["job_descriptions"].find_one({"id": jd_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Job Description not found")
    return JobDescriptionModel(**doc)

