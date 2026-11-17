import pytest
import os
from pathlib import Path
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.resume_extractor import parse_resume_content
from app.parsers.jd_extractor import extract_jd_entities
from app.parsers.skill_database import normalize_skill, extract_skills_from_text
from app.matching.scorer import evaluate_candidate
from app.models import WeightsConfig

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

def test_skill_alias_normalization():
    assert normalize_skill("aws") == "Amazon Web Services (AWS)"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("golang") == "Go / Golang"

def test_extract_skills_from_text():
    sample_text = "Proficient in Python, AWS, Docker, Kubernetes, and PostgreSQL with React frontends."
    skills = extract_skills_from_text(sample_text)
    assert "Python" in skills
    assert "Amazon Web Services (AWS)" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "PostgreSQL" in skills
    assert "React" in skills

def test_parse_sample_pdf_resume():
    pdf_path = SAMPLE_DIR / "01_Alex_Rivera_Senior_Backend.pdf"
    assert pdf_path.exists()
    
    with open(pdf_path, "rb") as f:
        bytes_data = f.read()

    raw_text, pages = extract_text_from_pdf(bytes_data, pdf_path.name)
    assert len(raw_text) > 100
    assert len(pages) >= 1

    candidate = parse_resume_content(raw_text, pdf_path.name, "cand_test_01")
    assert "Rivera" in candidate.name or "Alex" in candidate.name
    assert candidate.email == "alex.rivera@techcloud.io"
    assert "Python" in candidate.skills
    assert "Amazon Web Services (AWS)" in candidate.skills
    assert candidate.total_experience_years >= 5.0
    assert len(candidate.education) >= 1

def test_parse_sample_docx_resume():
    docx_path = SAMPLE_DIR / "02_Sophia_Chen_FullStack_Cloud.docx"
    assert docx_path.exists()

    with open(docx_path, "rb") as f:
        bytes_data = f.read()

    raw_text, paragraphs = extract_text_from_docx(bytes_data, docx_path.name)
    assert len(raw_text) > 100

    candidate = parse_resume_content(raw_text, docx_path.name, "cand_test_02")
    assert "Sophia" in candidate.name or "Chen" in candidate.name
    assert candidate.email == "sophia.chen@devmail.org"
    assert "React" in candidate.skills
    assert candidate.total_experience_years >= 4.0

def test_corrupted_file_handling():
    corrupted_path = SAMPLE_DIR / "12_Corrupted_Invalid_Sample.pdf"
    assert corrupted_path.exists()

    with open(corrupted_path, "rb") as f:
        bytes_data = f.read()

    with pytest.raises(ValueError) as excinfo:
        extract_text_from_pdf(bytes_data, corrupted_path.name)
    assert "corrupted" in str(excinfo.value).lower() or "invalid" in str(excinfo.value).lower()

def test_matching_algorithm_scoring():
    # Load Alex Rivera (Senior Backend)
    with open(SAMPLE_DIR / "01_Alex_Rivera_Senior_Backend.pdf", "rb") as f:
        alex_text, _ = extract_text_from_pdf(f.read(), "01_Alex_Rivera_Senior_Backend.pdf")
    alex_cand = parse_resume_content(alex_text, "01_Alex_Rivera_Senior_Backend.pdf", "cand_01")

    # Load James Wilson (Junior Dev)
    with open(SAMPLE_DIR / "07_James_Wilson_Junior_Developer.pdf", "rb") as f:
        james_text, _ = extract_text_from_pdf(f.read(), "07_James_Wilson_Junior_Developer.pdf")
    james_cand = parse_resume_content(james_text, "07_James_Wilson_Junior_Developer.pdf", "cand_07")

    # Load Senior Backend JD
    with open(SAMPLE_DIR / "Sample_JD_Senior_Backend_Engineer.txt", "r") as f:
        jd_text = f.read()
    jd = extract_jd_entities(jd_text, "Senior Backend Engineer", "CloudScale Technologies", "jd_01")

    # Match both against the Senior Backend JD
    alex_match = evaluate_candidate(alex_cand, jd)
    james_match = evaluate_candidate(james_cand, jd)

    # Alex should have a significantly higher score than Junior James
    assert alex_match.overall_score > james_match.overall_score
    assert alex_match.overall_score >= 80.0
    assert alex_match.status in ["Strong Fit", "Moderate Fit"]

    # Check component scores
    assert alex_match.component_scores["skills"] > james_match.component_scores["skills"]
    assert alex_match.component_scores["experience"] > james_match.component_scores["experience"]
    assert len(alex_match.reasons) >= 3
    assert len(alex_match.supporting_evidence) >= 2

def test_dynamic_weight_redistribution():
    # Create a JD without any education requirement
    jd_no_edu = extract_jd_entities(
        "Job Title: Software Engineer\nWe require Python and Docker with 3+ years experience. Build web apps.",
        "Software Engineer",
        "TestCo",
        "jd_no_edu"
    )
    # Ensure JD has no education requirements
    jd_no_edu.required_qualifications = []

    # Evaluate candidate
    with open(SAMPLE_DIR / "01_Alex_Rivera_Senior_Backend.pdf", "rb") as f:
        alex_text, _ = extract_text_from_pdf(f.read(), "01_Alex_Rivera_Senior_Backend.pdf")
    alex_cand = parse_resume_content(alex_text, "01_Alex_Rivera_Senior_Backend.pdf", "cand_01")

    result = evaluate_candidate(alex_cand, jd_no_edu)
    
    # Qualification weight should be 0, remaining weights redistributed to sum to 1.0
    assert result.applied_weights["qualification"] == 0.0
    assert round(sum(result.applied_weights.values()), 2) == 1.0
    assert result.applied_weights["skills"] > 0.40  # boosted proportionally

