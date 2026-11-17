import logging
from typing import List, Dict, Any, Tuple, Set
import numpy as np
from app.parsers.skill_database import normalize_skill
from app.matching.model_loader import encode_texts, compute_cosine_similarity
from app.config import settings

logger = logging.getLogger("resume_matcher.skill_matcher")

def match_skills(
    candidate_skills: List[str],
    jd_required_skills: List[str],
    jd_preferred_skills: List[str]
) -> Dict[str, Any]:
    """
    Hybrid skill matching:
    1. Canonical alias matching (100% credit)
    2. Embedding-based semantic similarity for synonyms/closely related technologies (partial credit)
    3. Preferred skills bonus boost
    """
    # Normalize candidate skills
    cand_norm_set: Set[str] = {normalize_skill(s) for s in candidate_skills}
    
    # Normalize JD required and preferred skills
    req_norm_list = [normalize_skill(s) for s in jd_required_skills]
    pref_norm_list = [normalize_skill(s) for s in jd_preferred_skills]

    matched_required: List[str] = []
    missing_required: List[str] = []
    fuzzy_matches: List[Dict[str, Any]] = []

    # 1. Exact / Canonical matching for required skills
    unmatched_required = []
    for req in req_norm_list:
        if req in cand_norm_set:
            matched_required.append(req)
        else:
            unmatched_required.append(req)

    # 2. Semantic matching for unmatched required skills
    if unmatched_required and candidate_skills:
        try:
            req_embeddings = encode_texts(unmatched_required)
            cand_skills_list = list(cand_norm_set)
            cand_embeddings = encode_texts(cand_skills_list)

            # Compute similarity matrix
            sim_matrix = np.dot(req_embeddings, cand_embeddings.T)
            # Normalize by norms
            req_norms = np.linalg.norm(req_embeddings, axis=1, keepdims=True)
            cand_norms = np.linalg.norm(cand_embeddings, axis=1, keepdims=True)
            sim_matrix = sim_matrix / (req_norms * cand_norms.T + 1e-9)

            for i, req in enumerate(unmatched_required):
                best_cand_idx = int(np.argmax(sim_matrix[i]))
                best_sim = float(sim_matrix[i, best_cand_idx])
                best_cand_skill = cand_skills_list[best_cand_idx]

                if best_sim >= settings.SEMANTIC_SKILL_THRESHOLD:
                    matched_required.append(req)
                    fuzzy_matches.append({
                        "required_skill": req,
                        "matched_to": best_cand_skill,
                        "similarity": round(best_sim, 3)
                    })
                else:
                    missing_required.append(req)
        except Exception as e:
            logger.warning(f"Semantic skill matching fallback: {e}")
            missing_required.extend(unmatched_required)
    else:
        missing_required.extend(unmatched_required)

    # 3. Preferred skills matching
    matched_preferred: List[str] = []
    for pref in pref_norm_list:
        if pref in cand_norm_set and pref not in matched_required:
            matched_preferred.append(pref)

    # Calculate skill score (0 - 100)
    total_req = len(req_norm_list)
    if total_req == 0:
        # If JD has no specified required skills, evaluate based on general tech skills density
        base_score = min(100.0, len(candidate_skills) * 8.0)
    else:
        exact_count = len(matched_required) - len(fuzzy_matches)
        fuzzy_count = len(fuzzy_matches)
        # Exact match gets 1.0 weight, fuzzy gets 0.8 weight
        effective_matched = (exact_count * 1.0) + (fuzzy_count * 0.8)
        base_score = (effective_matched / total_req) * 100.0

    # Preferred skills grant a bonus up to +15 points
    if pref_norm_list:
        pref_ratio = len(matched_preferred) / len(pref_norm_list)
        pref_bonus = pref_ratio * 15.0
        final_score = min(100.0, base_score + pref_bonus)
    else:
        final_score = min(100.0, base_score)

    return {
        "score": round(final_score, 2),
        "matched_skills": sorted(list(set(matched_required))),
        "missing_skills": sorted(list(set(missing_required))),
        "preferred_matched_skills": sorted(list(set(matched_preferred))),
        "fuzzy_matches": fuzzy_matches,
        "total_required_skills": total_req,
        "matched_required_count": len(matched_required)
    }

