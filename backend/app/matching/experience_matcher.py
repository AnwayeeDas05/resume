import logging
from typing import Dict, Any, List
from app.models import ResumeParsedModel, JobDescriptionModel

logger = logging.getLogger("resume_matcher.experience_matcher")

def match_experience(
    candidate: ResumeParsedModel,
    jd: JobDescriptionModel
) -> Dict[str, Any]:
    """
    Evaluates candidate's relevant years of experience against JD requirement.
    Uses continuous proportional scoring with graceful penalty curve.
    """
    cand_years = candidate.total_experience_years
    req_years = jd.required_experience_years

    # If JD doesn't state required years, default to 100 if candidate has at least 1 year
    if req_years <= 0:
        score = 100.0 if cand_years >= 1.0 else 85.0
        gap = 0.0
        assessment = "Requirement unspecified; candidate experience verified."
    else:
        gap = round(cand_years - req_years, 1)
        if cand_years >= req_years:
            # Full marks for meeting or exceeding
            score = 100.0
            assessment = f"Exceeds experience requirement by +{gap} yrs ({cand_years} vs {req_years} required)" if gap > 0 else f"Exactly meets required {req_years} years"
        else:
            # Ratio with smooth curve
            ratio = cand_years / req_years
            # Exponential decay rather than harsh drop
            score = max(10.0, ratio * 90.0)
            assessment = f"Below requirement by {abs(gap)} yrs ({cand_years} vs {req_years} required)"

    # Role Title Relevance Check
    jd_title_lower = jd.title.lower()
    title_matches = []
    for exp in candidate.experience_details:
        exp_title = (exp.title or "").lower()
        # Check title overlap
        common_words = set(jd_title_lower.split()) & set(exp_title.split())
        # Filter out common stop words
        common_substantive = {w for w in common_words if w not in {"and", "&", "of", "in", "the", "a"}}
        if len(common_substantive) >= 1:
            title_matches.append(exp.title)

    return {
        "score": round(score, 2),
        "candidate_years": cand_years,
        "required_years": req_years,
        "gap_years": gap,
        "assessment": assessment,
        "matching_role_titles": title_matches
    }

