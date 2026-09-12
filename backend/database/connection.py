"""
ResumeIQ v2 — Database Connection & Session Management
Supports PostgreSQL (production) and SQLite (development).
"""

import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from backend.config import get_settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        connect_args = {}
        if "sqlite" in settings.DATABASE_URL:
            connect_args["check_same_thread"] = False
        _engine = create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
        # Enable WAL mode for SQLite
        if "sqlite" in settings.DATABASE_URL:
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return _SessionLocal


def get_db() -> Session:
    """FastAPI dependency — yields a DB session."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    # Import all models so they register with Base
    import backend.database.models  # noqa: F401
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables created/verified")
