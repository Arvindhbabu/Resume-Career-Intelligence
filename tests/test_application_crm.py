"""
Unit tests for Job Discovery, Application CRM, and Next-Best-Action Engine.
"""

from backend.services.job_discovery_service import job_discovery_service
from backend.services.application_crm_service import application_crm_service
from backend.services.next_best_action_engine import next_best_action_engine


def test_job_discovery_feed():
    candidate_skills = ["python", "pytorch", "fastapi"]
    feed = job_discovery_service.fetch_personalized_feed(candidate_skills, "Data Scientist")

    assert len(feed) > 0
    assert "title" in feed[0]
    assert "priority_fit_score" in feed[0]
    assert feed[0]["priority_fit_score"] >= feed[-1]["priority_fit_score"]


def test_application_crm_lifecycle(db_session):
    # Create application
    app = application_crm_service.create_application(
        db_session,
        company_name="Google",
        job_title="Senior AI Engineer",
        status="Saved"
    )
    assert app.id is not None
    assert app.status == "Saved"

    # Transition stage
    updated = application_crm_service.update_stage(db_session, app.id, "Applied", "Submitted via Greenhouse portal")
    assert updated.status == "Applied"
    assert updated.applied_date is not None
    assert len(updated.events) == 2

    # Get Kanban board
    kanban = application_crm_service.get_kanban_board(db_session)
    assert "Applied" in kanban
    assert len(kanban["Applied"]) == 1

    # Analytics
    stats = application_crm_service.get_analytics(db_session)
    assert stats["total_applications"] >= 1
    assert stats["applied_count"] >= 1


def test_next_best_action_queue(db_session):
    actions = next_best_action_engine.generate_action_queue(db_session)
    assert len(actions) >= 3
    assert actions[0]["priority_score"] >= actions[1]["priority_score"]
    assert "action_type" in actions[0]
