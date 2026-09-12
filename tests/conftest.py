"""
Pytest configuration and shared fixtures for ResumeIQ test suite.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.connection import Base, get_db
import backend.database.connection as db_conn
from backend.main import create_app

# Shared in-memory SQLite URI so threads in TestClient see the exact same schema & tables
TEST_DB_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"

TEST_ENGINE = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=TEST_ENGINE)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

# Patch connection module so init_db() inside lifespan uses TEST_ENGINE
db_conn._engine = TEST_ENGINE
db_conn._SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh isolated database transaction/session per test."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database session."""
    app = create_app()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
