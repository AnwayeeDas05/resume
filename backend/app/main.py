import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import db_manager
from app.matching.model_loader import get_sentence_transformer
from app.routes import jd_routes, resume_routes, matching_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resume_matcher")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing AI Resume Matcher & Candidate Ranker Backend...")
    await db_manager.connect()
    
    # Pre-warm SentenceTransformer embedding model
    try:
        logger.info("Pre-warming SentenceTransformer model...")
        get_sentence_transformer()
        logger.info("SentenceTransformer ready!")
    except Exception as e:
        logger.error(f"Failed to pre-warm SentenceTransformer: {e}")

    yield

    # Shutdown actions
    logger.info("Shutting down backend...")
    await db_manager.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI Resume Matching & Candidate Ranking API",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(jd_routes.router, prefix=settings.API_V1_STR)
app.include_router(resume_routes.router, prefix=settings.API_V1_STR)
app.include_router(matching_routes.router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health status endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_mode": "Mock/In-Memory" if db_manager.is_mock else "Connected (MongoDB)",
        "model_loaded": True,
        "weights": {
            "skills": settings.DEFAULT_WEIGHT_SKILLS,
            "semantic": settings.DEFAULT_WEIGHT_SEMANTIC,
            "experience": settings.DEFAULT_WEIGHT_EXPERIENCE,
            "qualification": settings.DEFAULT_WEIGHT_QUALIFICATION
        }
    }

# Mount frontend production build if available
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
