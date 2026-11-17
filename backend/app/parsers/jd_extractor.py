import re
import logging
from typing import Dict, List, Any, Tuple
from app.parsers.skill_database import extract_skills_from_text
from app.models import JobDescriptionModel, WeightsConfig
from app.parsers.resume_extractor import EDUCATION_DEGREE_PATTERNS

logger = logging.getLogger("resume_matcher.jd_extractor")

EXPERIENCE_REQ_REGEX = re.compile(
    r'(?:minimum|at least|requires?|with)?\s*(\d+(?:\.\d+)?)\s*(?:\+|-|\s*to\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+relevant)?\s+(?:experience|work experience)',
    re.IGNORECASE
)

def extract_jd_entities(text: str, title: str, company: str, jd_id: str, weights: WeightsConfig = None) -> JobDescriptionModel:
    """
    Parses a Job Description text into structured requirements:
    - Required skills vs Preferred skills
    - Experience years required
    - Degree qualification levels
    - Key responsibilities
    """
    cleaned = text.strip()
    
    # Split text into sections if headers exist
    req_section = ""
    pref_section = ""
    resp_section = ""

    lines = cleaned.split('\n')
    current_mode = "overview"

    for line in lines:
        l_lower = line.strip().lower()
        if any(h in l_lower for h in ["preferred qualifications", "nice to have", "bonus points", "good to have", "desired skills"]):
            current_mode = "preferred"
        elif any(h in l_lower for h in ["requirements", "required qualifications", "minimum qualifications", "must have", "what we're looking for", "basic qualifications"]):
            current_mode = "required"
        elif any(h in l_lower for h in ["responsibilities", "what you'll do", "the role", "duties", "key responsibilities"]):
            current_mode = "responsibilities"
        
        if current_mode == "required":
            req_section += line + "\n"
        elif current_mode == "preferred":
            pref_section += line + "\n"
        elif current_mode == "responsibilities":
            resp_section += line + "\n"

    # If no separate sections found, treat whole text as required
    if not req_section.strip():
        req_section = cleaned

    required_skills = extract_skills_from_text(req_section)
    preferred_skills = [s for s in extract_skills_from_text(pref_section) if s not in required_skills]
    
    # If required_skills is empty, extract from entire text
    if not required_skills:
        all_skills = extract_skills_from_text(cleaned)
        required_skills = all_skills[:12]
        preferred_skills = all_skills[12:20]

    # Extract required years of experience
    exp_years = 0.0
    exp_matches = list(EXPERIENCE_REQ_REGEX.finditer(cleaned))
    if exp_matches:
        try:
            exp_years = float(exp_matches[0].group(1))
        except Exception:
            exp_years = 0.0
    else:
        # Fallback search for e.g. "5 years" or "3+ years"
        simple_m = re.search(r'(\d+)\+?\s*years?', cleaned, re.IGNORECASE)
        if simple_m:
            try:
                exp_years = float(simple_m.group(1))
            except Exception:
                exp_years = 0.0

    # Extract required educational qualifications
    req_qualifications: List[str] = []
    for pattern, norm_level in EDUCATION_DEGREE_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            if norm_level not in req_qualifications:
                req_qualifications.append(norm_level)

    # Extract responsibilities bullet points
    responsibilities: List[str] = []
    resp_source = resp_section if resp_section.strip() else cleaned
    for line in resp_source.split('\n'):
        line_clean = line.strip().lstrip('•-*0123456789. ')
        if len(line_clean) > 25 and not any(k in line_clean.lower() for k in ["requirement", "qualification", "benefit", "perk", "about us"]):
            responsibilities.append(line_clean)
            if len(responsibilities) >= 8:
                break

    return JobDescriptionModel(
        id=jd_id,
        title=title,
        company=company or "Company",
        raw_text=cleaned,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        required_experience_years=exp_years,
        required_qualifications=req_qualifications,
        responsibilities=responsibilities,
        weights=weights or WeightsConfig()
    )

