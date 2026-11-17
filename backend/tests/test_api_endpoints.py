import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from app.main import app

client = TestClient(app)

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "weights" in data

def test_create_and_get_job_description():
    payload = {
        "title": "Senior Cloud Backend Engineer",
        "company": "ScalePlatform Inc",
        "text": """Job Title: Senior Cloud Backend Engineer
Company: ScalePlatform Inc
Location: Remote

We need a Senior Cloud Backend Engineer.
Responsibilities:
• Build backend APIs in Python using FastAPI.
• Deploy services on AWS with Docker and Kubernetes.
• Manage PostgreSQL and Redis databases.

Requirements:
• 5+ years of software development experience.
• Hands-on proficiency with Python, FastAPI, Docker, and AWS.
• Strong database experience with PostgreSQL.
• Bachelor's degree in Computer Science or Software Engineering.

Nice to have:
• Kafka and Kubernetes experience.
"""
    }
    res = client.post("/api/jd", json=payload)
    assert res.status_code == 200
    jd_data = res.json()
    assert jd_data["id"].startswith("jd_")
    assert "Python" in jd_data["required_skills"]
    assert "Amazon Web Services (AWS)" in jd_data["required_skills"]
    assert jd_data["required_experience_years"] >= 5.0
    assert len(jd_data["responsibilities"]) >= 2

    # Fetch list
    list_res = client.get("/api/jd")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

def test_batch_resume_upload_with_corrupted_file():
    # Upload 3 files: 1 PDF, 1 DOCX, 1 corrupted PDF
    pdf_path = SAMPLE_DIR / "01_Alex_Rivera_Senior_Backend.pdf"
    docx_path = SAMPLE_DIR / "02_Sophia_Chen_FullStack_Cloud.docx"
    corrupted_path = SAMPLE_DIR / "12_Corrupted_Invalid_Sample.pdf"

    files = [
        ("files", (pdf_path.name, open(pdf_path, "rb"), "application/pdf")),
        ("files", (docx_path.name, open(docx_path, "rb"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ("files", (corrupted_path.name, open(corrupted_path, "rb"), "application/pdf")),
    ]

    res = client.post("/api/resumes/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["total_uploaded"] == 3
    assert data["successful_count"] == 2
    assert data["failed_count"] == 1
    assert len(data["failed_files"]) == 1
    assert "12_Corrupted" in data["failed_files"][0]["filename"]

def test_load_all_samples_and_run_matching():
    # Load all sample resumes (clean 100% valid load)
    load_res = client.post("/api/resumes/load-samples")
    assert load_res.status_code == 200
    load_data = load_res.json()
    assert load_data["successful_count"] >= 10
    assert load_data["failed_count"] == 0  # valid batch loads cleanly without false-alarm errors

    # Test explicit corrupted upload resilience endpoint
    corrupt_test_res = client.post("/api/resumes/test-corrupted-upload")
    assert corrupt_test_res.status_code == 200
    corrupt_data = corrupt_test_res.json()
    assert corrupt_data["failed_count"] >= 1
    assert "12_Corrupted" in corrupt_data["failed_files"][0]["filename"]

    # Create JD

    jd_res = client.post("/api/jd", json={
        "title": "Senior Backend Engineer",
        "company": "CloudScale Technologies",
        "text": (SAMPLE_DIR / "Sample_JD_Senior_Backend_Engineer.txt").read_text()
    })
    assert jd_res.status_code == 200
    jd_id = jd_res.json()["id"]

    # Run AI match & ranking
    match_res = client.post("/api/match", json={"jd_id": jd_id})
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["total_candidates"] >= 10
    
    # Check ranking order: highest overall_score first
    candidates = match_data["ranked_candidates"]
    for i in range(len(candidates) - 1):
        assert candidates[i]["overall_score"] >= candidates[i+1]["overall_score"]
        assert candidates[i]["rank"] == i + 1

    # Verify top candidate has high score and evidence
    top_cand = candidates[0]
    assert top_cand["overall_score"] >= 75.0
    assert len(top_cand["matched_skills"]) > 0
    assert len(top_cand["reasons"]) > 0
    assert len(top_cand["supporting_evidence"]) > 0

    # Test candidate analysis endpoint
    match_id = match_data["match_id"]
    cand_analysis_res = client.get(f"/api/match/{match_id}/candidate/{top_cand['candidate_id']}")
    assert cand_analysis_res.status_code == 200
    cand_analysis = cand_analysis_res.json()
    assert cand_analysis["candidate_name"] == top_cand["candidate_name"]
    assert "skills" in cand_analysis["component_scores"]
    assert "semantic" in cand_analysis["component_scores"]
    assert "experience" in cand_analysis["component_scores"]
    assert "qualification" in cand_analysis["component_scores"]

