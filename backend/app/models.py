from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)


class WeightsConfig(BaseModel):
    skills: float = Field(default=0.40, ge=0.0, le=1.0)
    semantic: float = Field(default=0.30, ge=0.0, le=1.0)
    experience: float = Field(default=0.20, ge=0.0, le=1.0)
    qualification: float = Field(default=0.10, ge=0.0, le=1.0)

    def normalized(self) -> "WeightsConfig":
        total = self.skills + self.semantic + self.experience + self.qualification
        if total <= 0:
            return WeightsConfig(skills=0.4, semantic=0.3, experience=0.2, qualification=0.1)
        return WeightsConfig(
            skills=round(self.skills / total, 4),
            semantic=round(self.semantic / total, 4),
            experience=round(self.experience / total, 4),
            qualification=round(self.qualification / total, 4)
        )


class ExperienceEntry(BaseModel):
    title: Optional[str] = "Professional"
    company: Optional[str] = ""
    duration: Optional[str] = ""
    years: float = 0.0
    description: Optional[str] = ""


class EducationEntry(BaseModel):
    degree: Optional[str] = ""
    field_of_study: Optional[str] = ""
    institution: Optional[str] = ""
    year: Optional[str] = ""
    normalized_level: Optional[str] = "Unknown"  # PhD, Master's, Bachelor's, Associate/Diploma


class ProjectEntry(BaseModel):
    title: Optional[str] = ""
    description: Optional[str] = ""
    technologies: List[str] = []


class JobDescriptionInput(BaseModel):
    title: str = Field(..., description="Job Title, e.g. Senior Backend Engineer")
    company: Optional[str] = "Acme Corp"
    text: str = Field(..., description="Full text of the Job Description")
    weights: Optional[WeightsConfig] = None


class JobDescriptionModel(BaseModel):
    id: str
    title: str
    company: Optional[str] = ""
    raw_text: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    required_experience_years: float = 0.0
    required_qualifications: List[str] = []
    responsibilities: List[str] = []
    weights: WeightsConfig = WeightsConfig()
    created_at: datetime = Field(default_factory=utc_now)


class ResumeParsedModel(BaseModel):
    id: str
    filename: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    links: List[str] = []
    location: Optional[str] = None
    skills: List[str] = []
    total_experience_years: float = 0.0
    experience_details: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    certifications: List[str] = []
    projects: List[ProjectEntry] = []
    summary: Optional[str] = ""
    raw_text: str
    created_at: datetime = Field(default_factory=utc_now)


class SupportingEvidence(BaseModel):
    category: str  # Skills, Semantic, Experience, Education
    snippet: str
    relevance_note: str


class CandidateMatchResult(BaseModel):
    candidate_id: str
    filename: str
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    overall_score: float  # 0 to 100
    rank: int = 1
    component_scores: Dict[str, float]  # skills, semantic, experience, qualification
    applied_weights: Dict[str, float]
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    preferred_matched_skills: List[str] = []
    candidate_experience_years: float = 0.0
    required_experience_years: float = 0.0
    candidate_education_level: str = "Unknown"
    required_education_level: str = "Any"
    supporting_evidence: List[SupportingEvidence] = []
    reasons: List[str] = []
    status: str = "Evaluated"  # Strong Fit, Moderate Fit, Potential Match, Low Match


class MatchRunResponse(BaseModel):
    match_id: str
    jd_id: str
    jd_title: str
    weights_used: WeightsConfig
    total_candidates: int
    ranked_candidates: List[CandidateMatchResult]
    processed_at: datetime = Field(default_factory=utc_now)


class BatchUploadResponse(BaseModel):
    total_uploaded: int
    successful_count: int
    failed_count: int
    successful_candidates: List[ResumeParsedModel]
    failed_files: List[Dict[str, str]]
