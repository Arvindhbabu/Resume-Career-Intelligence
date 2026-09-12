"""
Unit tests for Career Profile Service & Evidence Skill Graph.
"""

from backend.services.career_profile_service import career_profile_service
from backend.services.skill_graph_service import skill_graph_service
from backend.ai.skill_graph import skill_graph


def test_career_profile_crud(db_session):
    profile = career_profile_service.get_or_create_profile(db_session, user_token="test-token-123")
    assert profile is not None
    assert profile.user_token == "test-token-123"

    updated = career_profile_service.update_profile(
        db_session,
        profile.id,
        {
            "full_name": "Alice Johnson",
            "current_role": "Data Scientist",
            "target_roles": ["Senior Data Scientist", "AI Researcher"],
            "total_years_experience": 5.0,
        }
    )
    assert updated.full_name == "Alice Johnson"
    assert "AI Researcher" in updated.to_dict()["target_roles"]


def test_skill_evidence_graph_linking(db_session):
    profile = career_profile_service.get_or_create_profile(db_session, user_token="test-token-456")

    # Add evidence nodes
    ev1 = career_profile_service.add_skill_evidence(
        db_session,
        profile.id,
        skill_name="PyTorch",
        evidence_type="github_repo",
        source_title="DeepVision Project",
        confidence=0.95,
        proficiency="advanced"
    )
    assert ev1.id is not None
    assert ev1.canonical_name == "pytorch"

    ev2 = career_profile_service.add_skill_evidence(
        db_session,
        profile.id,
        skill_name="Python",
        evidence_type="resume",
        source_title="5 years experience at TechCorp",
        confidence=1.0,
        proficiency="expert"
    )
    assert ev2.canonical_name == "python"

    graph = career_profile_service.get_evidence_graph(db_session, profile.id)
    assert graph["total_skills"] >= 2
    assert "pytorch" in graph["skills"]
    assert graph["skills"]["pytorch"]["highest_proficiency"] == "advanced"


def test_skill_graph_service_coverage():
    evidence_list = [
        {"skill": "PyTorch", "canonical": "pytorch", "confidence": 0.95},
        {"skill": "Python", "canonical": "python", "confidence": 1.0},
    ]

    required = ["PyTorch", "Python", "AWS"]
    eval_res = skill_graph_service.evaluate_skills_against_evidence(required, evidence_list)

    assert eval_res["verified_skills_count"] == 2
    assert eval_res["unsupported_skills_count"] == 1
    assert eval_res["evidence_coverage_percent"] == 66.7
    assert eval_res["unsupported_skills"][0]["skill"] == "AWS"
