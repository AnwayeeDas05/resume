import logging
from typing import Dict, Any, List
from app.models import ResumeParsedModel, JobDescriptionModel

logger = logging.getLogger("resume_matcher.qualification_matcher")

DEGREE_HIERARCHY = {
    "PhD": 4,
    "Master's": 3,
    "Bachelor's": 2,
    "Associate/Diploma": 1,
    "Unknown": 0
}

RELEVANT_STEM_FIELDS = [
    "computer science", "software engineering", "computer engineering", "information technology",
    "data science", "artificial intelligence", "mathematics", "electrical engineering",
    "physics", "statistics", "information systems"
]

def match_qualification(
    candidate: ResumeParsedModel,
    jd: JobDescriptionModel
) -> Dict[str, Any]:
    """
    Compares candidate's highest educational attainment and field of study against JD.
    """
    # Find candidate's highest degree
    highest_cand_level = "Unknown"
    highest_cand_rank = 0
    candidate_field = ""

    for edu in candidate.education:
        level = edu.normalized_level or "Unknown"
        rank = DEGREE_HIERARCHY.get(level, 0)
        if rank > highest_cand_rank:
            highest_cand_rank = rank
            highest_cand_level = level
            candidate_field = edu.field_of_study or ""

    # Find JD required degree level
    req_qualifications = jd.required_qualifications
    if not req_qualifications:
        # JD did not specify explicit degree requirement
        return {
            "score": 100.0 if highest_cand_rank >= 1 else 90.0,
            "candidate_level": highest_cand_level,
            "required_level": "Unspecified / Open",
            "is_specified_in_jd": False,
            "field_relevance": "N/A"
        }

    # Highest requirement in JD
    highest_req_level = "Bachelor's"
    highest_req_rank = 2
    for q in req_qualifications:
        rank = DEGREE_HIERARCHY.get(q, 0)
        if rank > highest_req_rank:
            highest_req_rank = rank
            highest_req_level = q

    # Check field of study relevance
    field_relevant = any(f in candidate_field.lower() for f in RELEVANT_STEM_FIELDS)

    if highest_cand_rank >= highest_req_rank:
        score = 100.0
    elif highest_cand_rank == highest_req_rank - 1:
        # e.g. candidate has Bachelor's when Master's requested
        score = 85.0 if field_relevant else 75.0
    elif highest_cand_rank > 0:
        score = 65.0
    else:
        score = 40.0

    return {
        "score": round(score, 2),
        "candidate_level": highest_cand_level,
        "required_level": highest_req_level,
        "is_specified_in_jd": True,
        "field_relevance": "Direct STEM / Relevant" if field_relevant else "Domain-Adjacent"
    }

