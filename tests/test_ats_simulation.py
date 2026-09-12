"""
Unit tests for Platform-Aware ATS Simulation & Resume Intelligence Engine.
"""

from backend.services.ats_simulation_engine import ats_simulation_engine
from backend.services.resume_intelligence_service import resume_intelligence_service


def test_multi_dimensional_scoring():
    parsed_sample = {
        "raw_text": "John Doe\nSoftware Engineer\ndeveloped PyTorch pipeline improving accuracy by 34%.\nBuilt REST API using FastAPI and PostgreSQL.",
        "skills": ["python", "pytorch", "fastapi", "postgresql", "rest api"],
        "section_flags": {"summary": True, "experience": True, "education": True, "skills": True},
        "email": "john@example.com",
        "phone": "+1234567890",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe",
    }

    scores = ats_simulation_engine.calculate_multi_dimensional_scores(parsed_sample)

    assert scores["resume_quality"] > 80.0
    assert scores["ats_parseability"] >= 90.0
    assert scores["recruiter_impact"] > 60.0
    assert scores["application_readiness"] > 70.0


def test_platform_aware_ats_simulations():
    parsed_sample = {
        "raw_text": "Jane Smith\nData Scientist 2020 - 2024\nDeveloped PyTorch models for video classification.\nJane@example.com 555-0199",
        "skills": ["python", "pytorch", "data science", "machine learning"],
        "section_flags": {"experience": True, "education": True, "skills": True},
        "email": "jane@example.com",
        "phone": "555-0199",
    }

    base_scores = ats_simulation_engine.calculate_multi_dimensional_scores(parsed_sample)
    simulations = ats_simulation_engine.simulate_platform_profiles(parsed_sample, base_scores)

    assert "Workday" in simulations
    assert "Greenhouse" in simulations
    assert "Lever" in simulations
    assert "Taleo" in simulations
    assert "iCIMS" in simulations
    assert "SuccessFactors" in simulations

    for platform, result in simulations.items():
        assert 0 <= result["score"] <= 100
        assert "fit" in result
        assert "notes" in result


def test_achievement_extraction():
    sample_text = """
    Work Experience:
    - Increased model training throughput by 45% using distributed PyTorch.
    - Spearheaded API migration resulting in $120K annual cost reduction.
    - Attended team meetings and wrote standard documentation.
    """
    achievements = resume_intelligence_service.extract_quantified_achievements(sample_text)
    assert len(achievements) == 2
    assert "45%" in achievements[0]
    assert "$120K" in achievements[1]
