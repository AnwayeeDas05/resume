import logging
from typing import Dict, Any, List, Optional
from app.models import (
    ResumeParsedModel,
    JobDescriptionModel,
    CandidateMatchResult,
    SupportingEvidence,
    WeightsConfig
)
from app.matching.skill_matcher import match_skills
from app.matching.semantic_matcher import match_semantic_similarity
from app.matching.experience_matcher import match_experience
from app.matching.qualification_matcher import match_qualification

logger = logging.getLogger("resume_matcher.scorer")

def evaluate_candidate(
    candidate: ResumeParsedModel,
    jd: JobDescriptionModel,
    custom_weights: Optional[WeightsConfig] = None
) -> CandidateMatchResult:
    """
    Computes hybrid multi-criteria match score for a candidate against a job description.
    Enforces demographic exclusion and dynamic weight redistribution when JD categories are absent.
    """
    # 1. Execute individual component matchers
    skill_res = match_skills(
        candidate_skills=candidate.skills,
        jd_required_skills=jd.required_skills,
        jd_preferred_skills=jd.preferred_skills
    )
    semantic_res = match_semantic_similarity(candidate, jd)
    exp_res = match_experience(candidate, jd)
    qual_res = match_qualification(candidate, jd)

    # 2. Base weights (either custom or from JD or default 40/30/20/10)
    w = custom_weights or jd.weights or WeightsConfig()
    w_skills = w.skills
    w_semantic = w.semantic
    w_experience = w.experience
    w_qualification = w.qualification

    # 3. Dynamic weight redistribution if a JD requirement category is absent:
    # Check if education was completely unstated in JD
    is_qual_present = bool(jd.required_qualifications)
    # Check if experience years was completely unstated in JD
    is_exp_present = jd.required_experience_years > 0
    # Check if skills were present
    is_skills_present = bool(jd.required_skills)

    active_weights = {
        "skills": w_skills if is_skills_present else 0.0,
        "semantic": w_semantic,  # semantic similarity is always present
        "experience": w_experience if is_exp_present else 0.0,
        "qualification": w_qualification if is_qual_present else 0.0
    }

    # Redistribute proportionally to sum to 1.0
    active_sum = sum(active_weights.values())
    if active_sum <= 0:
        applied_weights = {"skills": 0.40, "semantic": 0.30, "experience": 0.20, "qualification": 0.10}
    else:
        applied_weights = {
            k: round(v / active_sum, 4) for k, v in active_weights.items()
        }

    # 4. Calculate overall weighted score (0 - 100)
    s_skills = skill_res["score"]
    s_semantic = semantic_res["score"]
    s_exp = exp_res["score"]
    s_qual = qual_res["score"]

    overall_score = (
        (s_skills * applied_weights["skills"]) +
        (s_semantic * applied_weights["semantic"]) +
        (s_exp * applied_weights["experience"]) +
        (s_qual * applied_weights["qualification"])
    )
    overall_score = max(0.0, min(100.0, round(overall_score, 1)))

    # 5. Determine qualification status badge
    if overall_score >= 82.0:
        status = "Strong Fit"
    elif overall_score >= 68.0:
        status = "Moderate Fit"
    elif overall_score >= 50.0:
        status = "Potential Match"
    else:
        status = "Low Match"

    # 6. Generate supporting evidence snippets
    evidence: List[SupportingEvidence] = []
    
    # Skills evidence
    if skill_res["matched_skills"]:
        sample_matched = ", ".join(skill_res["matched_skills"][:5])
        evidence.append(SupportingEvidence(
            category="Skills Match",
            snippet=f"Candidate verified proficiency in: {sample_matched}",
            relevance_note=f"Matched {len(skill_res['matched_skills'])} of {skill_res['total_required_skills']} target skills."
        ))

    # Experience evidence
    if candidate.experience_details:
        top_exp = candidate.experience_details[0]
        evidence.append(SupportingEvidence(
            category="Work Experience",
            snippet=f"{top_exp.title} ({top_exp.duration}): {top_exp.description[:200]}...",
            relevance_note=exp_res["assessment"]
        ))

    # Semantic evidence
    if candidate.summary:
        evidence.append(SupportingEvidence(
            category="Semantic Relevance",
            snippet=f"Summary: {candidate.summary[:200]}...",
            relevance_note=f"High contextual alignment (raw cosine {semantic_res['raw_similarity']}) with JD responsibilities."
        ))

    # Education evidence
    if candidate.education:
        top_edu = candidate.education[0]
        evidence.append(SupportingEvidence(
            category="Educational Qualification",
            snippet=f"{top_edu.degree} in {top_edu.field_of_study} ({top_edu.year or 'Completed'})",
            relevance_note=f"Level: {qual_res['candidate_level']} vs JD Required: {qual_res['required_level']} ({qual_res['field_relevance']})"
        ))

    # 7. Generate explainable reasons behind the score
    reasons: List[str] = []
    
    # Skills reasoning
    if skill_res["total_required_skills"] > 0:
        pct = int(skill_res["score"])
        reasons.append(
            f"Skills Alignment ({pct}%): Matched {len(skill_res['matched_skills'])} required skills. "
            f"{'Missing key skills: ' + ', '.join(skill_res['missing_skills'][:4]) if skill_res['missing_skills'] else 'All core required skills satisfied.'}"
        )
    else:
        reasons.append(f"Skills Density ({int(skill_res['score'])}%): Identified {len(candidate.skills)} relevant technical competencies.")

    # Semantic reasoning
    reasons.append(
        f"Semantic Content Fit ({int(s_semantic)}%): Section embeddings show {round(semantic_res['raw_similarity']*100, 1)}% contextual alignment between candidate experience and JD responsibilities."
    )

    # Experience reasoning
    if is_exp_present:
        reasons.append(
            f"Experience Match ({int(s_exp)}%): Candidate has {candidate.total_experience_years} years vs required {jd.required_experience_years} years. ({exp_res['assessment']})"
        )
    else:
        reasons.append(
            f"Experience History ({int(s_exp)}%): Candidate brings {candidate.total_experience_years} years of accumulated professional experience."
        )

    # Education reasoning
    reasons.append(
        f"Qualification ({int(s_qual)}%): Holds {qual_res['candidate_level']} degree. {qual_res['field_relevance']}."
    )

    return CandidateMatchResult(
        candidate_id=candidate.id,
        filename=candidate.filename,
        candidate_name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        overall_score=overall_score,
        rank=1,  # will be assigned by ranker
        component_scores={
            "skills": s_skills,
            "semantic": s_semantic,
            "experience": s_exp,
            "qualification": s_qual
        },
        applied_weights=applied_weights,
        matched_skills=skill_res["matched_skills"],
        missing_skills=skill_res["missing_skills"],
        preferred_matched_skills=skill_res["preferred_matched_skills"],
        candidate_experience_years=candidate.total_experience_years,
        required_experience_years=jd.required_experience_years,
        candidate_education_level=qual_res["candidate_level"],
        required_education_level=qual_res["required_level"],
        supporting_evidence=evidence,
        reasons=reasons,
        status=status
    )

