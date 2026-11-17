import uuid
import logging
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.models import (
    MatchRunResponse,
    CandidateMatchResult,
    WeightsConfig,
    JobDescriptionModel,
    ResumeParsedModel
)
from app.matching.scorer import evaluate_candidate
from app.database import db_manager

logger = logging.getLogger("resume_matcher.matching_routes")

router = APIRouter(prefix="/match", tags=["Matching & Ranking"])

class MatchRequest(BaseModel):
    jd_id: str
    candidate_ids: Optional[List[str]] = None
    custom_weights: Optional[WeightsConfig] = None

@router.post("", response_model=MatchRunResponse)
async def run_matching(payload: MatchRequest):
    """
    Executes hybrid AI matching of candidates against a Job Description.
    Applies configurable weights (Skills 40%, Semantic 30%, Experience 20%, Qualification 10%),
    normalizes skill aliases, section-aware sentence embeddings, and ranks candidates
    in descending order of overall score.
    """
    db = db_manager.get_db()
    
    # 1. Fetch JD
    jd_doc = await db["job_descriptions"].find_one({"id": payload.jd_id})
    if not jd_doc:
        raise HTTPException(status_code=404, detail=f"Job Description with ID '{payload.jd_id}' not found.")
    jd = JobDescriptionModel(**jd_doc)

    # 2. Fetch candidates
    if payload.candidate_ids:
        cursor = db["resumes"].find({"id": {"$in": payload.candidate_ids}})
    else:
        cursor = db["resumes"].find()
    
    cand_docs = await cursor.to_list(500)
    if not cand_docs:
        raise HTTPException(status_code=400, detail="No candidates found in database to match against.")

    # Deduplicate candidates so each individual resume appears exactly once in rankings
    seen_keys = set()
    candidates: List[ResumeParsedModel] = []
    for doc in cand_docs:
        cand = ResumeParsedModel(**doc)
        key = cand.filename or cand.email or cand.name
        if key not in seen_keys:
            seen_keys.add(key)
            candidates.append(cand)


    # 3. Evaluate each candidate
    match_results: List[CandidateMatchResult] = []
    for cand in candidates:
        try:
            result = evaluate_candidate(
                candidate=cand,
                jd=jd,
                custom_weights=payload.custom_weights
            )
            match_results.append(result)
        except Exception as e:
            logger.error(f"Error evaluating candidate {cand.name} ({cand.id}): {e}")

    # 4. Sort descending by overall matching score
    match_results.sort(key=lambda r: r.overall_score, reverse=True)

    # 5. Assign ranks
    for rank_idx, res in enumerate(match_results, start=1):
        res.rank = rank_idx

    match_id = f"match_{uuid.uuid4().hex[:10]}"
    active_weights = payload.custom_weights or jd.weights or WeightsConfig()

    response = MatchRunResponse(
        match_id=match_id,
        jd_id=jd.id,
        jd_title=jd.title,
        weights_used=active_weights.normalized(),
        total_candidates=len(match_results),
        ranked_candidates=match_results
    )

    # Store in database
    await db["matches"].insert_one(response.model_dump())

    return response

@router.get("/{match_id}", response_model=MatchRunResponse)
async def get_match_run(match_id: str):
    """Retrieves ranked results for a match run."""
    db = db_manager.get_db()
    doc = await db["matches"].find_one({"match_id": match_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Match run not found.")
    return MatchRunResponse(**doc)

@router.get("/{match_id}/candidate/{candidate_id}", response_model=CandidateMatchResult)
async def get_candidate_analysis(match_id: str, candidate_id: str):
    """
    Returns deep candidate-level analysis for a specific match run:
    component scores, matched/missing skills, supporting evidence, and reasoning.
    """
    db = db_manager.get_db()
    doc = await db["matches"].find_one({"match_id": match_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Match run not found.")
    
    match_run = MatchRunResponse(**doc)
    for cand in match_run.ranked_candidates:
        if cand.candidate_id == candidate_id:
            return cand
            
    raise HTTPException(status_code=404, detail="Candidate not found in this match run.")

@router.get("", response_model=List[MatchRunResponse])
async def list_match_runs():
    """Lists recent match runs."""
    db = db_manager.get_db()
    cursor = db["matches"].find().sort("processed_at", -1)
    results = await cursor.to_list(50)
    return [MatchRunResponse(**doc) for doc in results]

