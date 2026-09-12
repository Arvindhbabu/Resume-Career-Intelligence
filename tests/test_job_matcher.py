"""
Unit tests for Job Description Intelligence & Explainable Matcher.
"""

from backend.services.job_intelligence_service import job_intelligence_service
from backend.services.explainable_matcher_service import explainable_matcher_service


def test_job_description_parsing():
    sample_jd = """
    Senior Data Scientist - AI Platform
    We are looking for a Senior Data Scientist with minimum 4+ years experience.
    Must have proven experience in Python, PyTorch, SQL, and Machine Learning.
    Preferred skills include Kubernetes, Docker, and AWS deployment.
    Responsibilities include building deep learning models for production scale.
    """

    parsed = job_intelligence_service.parse_and_classify_jd(sample_jd, "Senior Data Scientist", "AI Platform")

    assert parsed["seniority"] == "Senior"
    assert parsed["years_required"] == 4.0
    assert "python" in parsed["skills"]
    assert "pytorch" in parsed["skills"]
    assert len(parsed["hard_requirements"]) > 0


def test_explainable_match_calculation():
    candidate_skills = ["python", "pytorch", "sql", "pandas"]
    candidate_exp = 5.0

    job_parsed = {
        "years_required": 4.0,
        "hard_skills": ["python", "pytorch", "sql"],
        "important_skills": ["pandas", "machine learning"],
        "preferred_skills": ["kubernetes", "aws"],
        "skills": ["python", "pytorch", "sql", "pandas", "machine learning", "kubernetes", "aws"],
    }

    match_res = explainable_matcher_service.match_resume_to_job(candidate_skills, candidate_exp, job_parsed)

    assert match_res["overall_match"] > 70.0
    assert match_res["recommendation"] in ["APPLY NOW", "APPLY AFTER TAILORING"]
    assert "python" in match_res["matched_skills"]
    assert "kubernetes" in match_res["missing_skills"]
    assert len(match_res["explanation"]["why_you_match"]) > 0
