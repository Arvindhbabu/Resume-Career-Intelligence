"""
ResumeIQ v2 — Centralized Configuration
Uses pydantic-settings for environment variable management.
"""

import os
from pathlib import Path
from functools import lru_cache

# ── Project paths ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
FAISS_DIR = DATA_DIR / "faiss_index"

# Ensure directories exist
for d in [DATA_DIR, UPLOAD_DIR, FAISS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / ".env")

        # ── Core ─────────────────────────────────────────────────────────────
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'resumeiq_v2.db'}"
        ).replace("postgres://", "postgresql://")

        # ── LLM Configuration ────────────────────────────────────────────────
        self.OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
        self.GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

        # ── Embeddings ───────────────────────────────────────────────────────
        self.EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.EMBEDDING_DIM: int = 384  # MiniLM-L6 outputs 384-dim vectors

        # ── FAISS ────────────────────────────────────────────────────────────
        self.FAISS_INDEX_PATH: str = str(FAISS_DIR)

        # ── Upload ───────────────────────────────────────────────────────────
        self.MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
        self.UPLOAD_DIR: str = str(UPLOAD_DIR)
        self.ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".doc", ".txt"}

        # ── Skill Graph ──────────────────────────────────────────────────────
        self.SKILL_ONTOLOGY_PATH: str = str(DATA_DIR / "skill_ontology.json")

        # ── Auth & Security ──────────────────────────────────────────────────
        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", self.SECRET_KEY)
        self.JWT_ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

        # ── Agent defaults ───────────────────────────────────────────────────
        self.AGENT_TIMEOUT: int = 30  # seconds
        self.LLM_MAX_TOKENS: int = 2000
        self.LLM_TEMPERATURE: float = 0.3

    @property
    def has_llm(self) -> bool:
        """Check if any LLM API key is configured."""
        return bool(self.OPENAI_API_KEY or self.GEMINI_API_KEY)

    @property
    def llm_provider(self) -> str:
        """Return the active LLM provider name."""
        if self.OPENAI_API_KEY:
            return "openai"
        elif self.GEMINI_API_KEY:
            return "gemini"
        return "none"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
