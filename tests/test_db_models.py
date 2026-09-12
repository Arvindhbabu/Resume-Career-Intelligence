"""
Unit tests for ResumeIQ 18 Database Models.
"""

import json
from backend.database.models import (
    User, CareerProfile, SkillEvidence, Resume, ResumeVersion, Analysis,
    SkillMapping, Job, JobRequirement, JobMatch, Application, ApplicationEvent,
    Interview, InterviewQuestion, PortfolioRepo, CareerGoal, NextBestAction
)

def test_user_and_career_profile(db_session):
    user = User(email="dataengineer@resumeiq.ai", password_hash="hashed_pw", full_name="Data Eng")
    db_session.add(user)
    db_session.flush()

    profile = CareerProfile(
        user_id=user.id,
        full_name="Data Eng",
        current_role="Junior Data Engineer",
        target_roles=json.dumps(["Senior Data Engineer", "Data Architect"]),
        total_years_experience=3.5
    )
    db_session.add(profile)
    db_session.commit()

    saved_user = db_session.query(User).filter_by(email="dataengineer@resumeiq.ai").first()
    assert saved_user is not None
    assert saved_user.profile is not None
    assert saved_user.profile.total_years_experience == 3.5
    assert "Senior Data Engineer" in saved_user.profile.to_dict()["target_roles"]


def test_evidence_graph_model(db_session):
    profile = CareerProfile(full_name="ML Specialist")
    db_session.add(profile)
    db_session.flush()

    evidence = SkillEvidence(
        profile_id=profile.id,
        skill_name="PyTorch",
        canonical_name="PyTorch",
        category="machine_learning",
        evidence_type="github_repo",
        source_title="VideoClassifier Repo",
        confidence=0.95,
        proficiency="advanced"
    )
    db_session.add(evidence)
    db_session.commit()

    saved_evidence = db_session.query(SkillEvidence).filter_by(skill_name="PyTorch").first()
    assert saved_evidence is not None
    assert saved_evidence.proficiency == "advanced"
    assert saved_evidence.to_dict()["confidence"] == 0.95


def test_job_and_application_pipeline(db_session):
    job = Job(
        title="Senior Python Developer",
        company="Tech Corp",
        location="Remote",
        description_raw="We are looking for Python, FastAPI, PostgreSQL expertise."
    )
    db_session.add(job)
    db_session.flush()

    app = Application(
        company_name="Tech Corp",
        job_title="Senior Python Developer",
        status="Applied",
        job_id=job.id
    )
    db_session.add(app)
    db_session.commit()

    saved_app = db_session.query(Application).filter_by(company_name="Tech Corp").first()
    assert saved_app is not None
    assert saved_app.status == "Applied"
