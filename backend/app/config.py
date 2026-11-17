import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "AI Resume Matcher & Candidate Ranker"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # MongoDB Settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "resume_matcher_db")
    USE_MOCK_DB_IF_UNAVAILABLE: bool = True

    # Directories
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    SAMPLES_DIR: Path = BASE_DIR / "sample_resumes"

    # NLP & AI Model Settings
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    SPACY_MODEL: str = "en_core_web_sm"

    # Default Hybrid Matching Weights (Must sum to 1.0)
    DEFAULT_WEIGHT_SKILLS: float = 0.40
    DEFAULT_WEIGHT_SEMANTIC: float = 0.30
    DEFAULT_WEIGHT_EXPERIENCE: float = 0.20
    DEFAULT_WEIGHT_QUALIFICATION: float = 0.10

    # Similarity Thresholds
    SEMANTIC_SKILL_THRESHOLD: float = 0.72

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

