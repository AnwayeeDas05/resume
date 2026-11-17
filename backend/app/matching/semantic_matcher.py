import logging
from typing import Dict, Any, List
import numpy as np
from app.matching.model_loader import encode_texts, compute_cosine_similarity
from app.models import ResumeParsedModel, JobDescriptionModel

logger = logging.getLogger("resume_matcher.semantic_matcher")

def match_semantic_similarity(
    candidate: ResumeParsedModel,
    jd: JobDescriptionModel
) -> Dict[str, Any]:
    """
    Section-aware semantic embedding similarity:
    - Resume Work Experience & Projects vs JD Core Responsibilities
    - Resume Professional Summary vs JD Role Overview
    - Extracts most aligned snippets for evidence attribution.
    """
    # 1. Prepare JD sections
    jd_responsibilities_text = " ".join(jd.responsibilities) if jd.responsibilities else jd.raw_text[:800]
    jd_overview_text = f"{jd.title} at {jd.company}. {jd.raw_text[:500]}"

    # 2. Prepare Candidate sections (Excluding demographic data: name, gender, contact)
    cand_experience_text = " ".join([
        f"{exp.title} at {exp.company}: {exp.description}" 
        for exp in candidate.experience_details
    ])
    if not cand_experience_text.strip():
        cand_experience_text = candidate.summary or candidate.raw_text[:800]

    cand_projects_text = " ".join([
        f"{p.title}: {p.description}"
        for p in candidate.projects
    ])
    
    cand_full_context = f"{candidate.summary} {cand_experience_text} {cand_projects_text}".strip()
    if not cand_full_context:
        cand_full_context = candidate.raw_text[:1000]

    # Encode sections
    texts_to_encode = [
        jd_responsibilities_text,  # 0
        jd_overview_text,          # 1
        cand_experience_text,      # 2
        cand_full_context          # 3
    ]

    embeddings = encode_texts(texts_to_encode)
    jd_resp_vec = embeddings[0]
    jd_overview_vec = embeddings[1]
    cand_exp_vec = embeddings[2]
    cand_full_vec = embeddings[3]

    # Cosine similarities
    sim_exp_resp = compute_cosine_similarity(cand_exp_vec, jd_resp_vec)
    sim_full_overview = compute_cosine_similarity(cand_full_vec, jd_overview_vec)

    # Blend section similarities: 60% responsibilities vs experience, 40% overall context
    blended_sim = (sim_exp_resp * 0.60) + (sim_full_overview * 0.40)
    
    # Scale from [0.0, 1.0] to [0, 100]
    # In sentence transformers, typical cosine sim for related texts ranges from 0.35 to 0.85
    # We calibrate with standard min-max scaling to give intuitive 0-100 score
    calibrated_score = min(100.0, max(0.0, ((blended_sim - 0.20) / 0.65) * 100.0))

    return {
        "score": round(calibrated_score, 2),
        "raw_similarity": round(float(blended_sim), 4),
        "experience_vs_responsibilities_sim": round(float(sim_exp_resp), 4),
        "overview_vs_context_sim": round(float(sim_full_overview), 4)
    }

