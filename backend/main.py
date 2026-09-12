"""
ResumeIQ v2 — FastAPI Application
Main entry point with CORS, middleware, and lifespan events.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.config import get_settings, BASE_DIR

# ── Logging ──────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("resumeiq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    settings = get_settings()
    logger.info("🚀 ResumeIQ v2 starting up...")
    logger.info(f"   Database:  {settings.DATABASE_URL[:50]}...")
    logger.info(f"   LLM:       {settings.llm_provider}")
    logger.info(f"   Embedding: {settings.EMBEDDING_MODEL}")

    # ── Initialize database ─────────────────────────────────────────────────
    from backend.database.connection import init_db, get_session_factory
    from backend.database.models import RecruiterDecision, FeedbackEntry
    from backend.ai.recruiter_learning import recruiter_engine
    from backend.ai.feedback_loop import feedback_loop

    init_db()
    logger.info("   Database initialized ✓")

    # ── Synchronize ResumeIQ Intelligence ────────────────────────────────────
    SessionLocal = get_session_factory()
    with SessionLocal() as db:
        # Load Decisions
        decisions = db.query(RecruiterDecision).all()
        recruiter_engine.load_from_db([d.to_dict() for d in decisions])

        # Load Feedback
        feedback = db.query(FeedbackEntry).all()
        feedback_loop.load_from_db([f.to_dict() for f in feedback])

    yield  # ← App runs here

    logger.info("🛑 ResumeIQ v2 shutting down...")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title="ResumeIQ v2 — Intelligent Hiring Co-Pilot",
        description=(
            "Adaptive AI Hiring System with Self-Learning Skill Graph, "
            "Multi-Agent Reasoning, Bias-Aware Ranking & Explainable AI Scoring."
        ),
        version="2.0.0",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── API Routes ───────────────────────────────────────────────────────────
    from backend.api.auth_routes import router as auth_router
    from backend.api.v1_routes import router as v1_router
    from backend.api.v2_routes import router as api_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(v1_router, prefix="/api/v1")
    app.include_router(api_router, prefix="/api/v2")

    # ── Serve React frontend (production build) ──────────────────────────────
    frontend_dist = BASE_DIR / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve React SPA — all non-API routes go to index.html."""
            file_path = frontend_dist / full_path
            if file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_dist / "index.html"))
    else:
        @app.get("/")
        async def root():
            return {
                "message": "ResumeIQ v2 API is running",
                "docs": "/docs",
                "version": "2.0.0",
                "frontend": "Run 'cd frontend && npm run dev' for the dashboard",
            }

    return app


# ── Direct run ───────────────────────────────────────────────────────────────────
app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
