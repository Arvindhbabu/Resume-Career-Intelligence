"""
Unit tests for Interview Intelligence, Consistency Risk Checker, and GitHub Portfolio Intelligence.
"""

from backend.services.interview_intelligence_service import interview_intelligence_service
from backend.services.portfolio_intelligence_service import portfolio_intelligence_service


def test_resume_to_interview_consistency_detection():
    # Resume contains an unbacked complex claim
    resume_claims = [
        "Implemented distributed multi-node LLM training serving petabyte scale traffic.",
        "Built REST API in Python using FastAPI."
    ]
    candidate_evidence = [
        {"skill": "Python", "snippet": "built REST API in Python"},
    ]

    res = interview_intelligence_service.analyze_resume_consistency(resume_claims, candidate_evidence)

    assert res["risky_claims_count"] == 1
    assert res["risky_claims"][0]["risk_level"] == "HIGH INTERVIEW RISK"
    assert "distributed" in res["risky_claims"][0]["claim"]


def test_interview_pack_generation(db_session):
    pack = interview_intelligence_service.generate_interview_pack(
        db_session,
        role_title="Senior ML Engineer",
        company_name="Anthropic",
        resume_text="Senior ML Engineer with PyTorch and Python experience.",
        skills=["python", "pytorch"],
        evidence_list=[]
    )

    assert pack["interview_id"] is not None
    assert len(pack["questions"]) >= 3
    categories = [q["category"] for q in pack["questions"]]
    assert "technical" in categories
    assert "project" in categories


def test_portfolio_repository_analysis(db_session):
    repo = portfolio_intelligence_service.analyze_repository(
        db_session,
        repo_url="https://github.com/user/deepvision",
        repo_name="deepvision",
        readme_text="DeepVision AI - Video Classification with PyTorch, Docker, pytest, and GitHub Actions."
    )

    assert repo.id is not None
    scores = repo.to_dict()["scores"]
    assert scores["testing"] >= 80.0
    assert scores["deployment"] >= 80.0
    assert len(repo.to_dict()["resume_bullet_suggestions"]) >= 1
