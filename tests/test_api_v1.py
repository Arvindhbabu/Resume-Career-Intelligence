"""
Integration API tests for ResumeIQ OS API v1 endpoints.
"""


def test_career_profile_api(client):
    resp = client.get("/api/v1/career-profile?user_token=test-api-token")
    assert resp.status_code == 200
    data = resp.json()
    assert "profile" in data
    assert "evidence_graph" in data

    update_payload = {
        "full_name": "API Test Candidate",
        "current_role": "Senior Engineer",
        "target_roles": ["Lead Engineer"]
    }
    update_resp = client.put("/api/v1/career-profile?user_token=test-api-token", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["full_name"] == "API Test Candidate"


def test_job_parse_and_match_api(client):
    jd_payload = {
        "raw_jd": "Must have Python and PyTorch. Senior Data Scientist role.",
        "title": "Senior Data Scientist",
        "company": "ScaleAI"
    }
    parse_resp = client.post("/api/v1/jobs/parse", json=jd_payload)
    assert parse_resp.status_code == 200
    parsed = parse_resp.json()
    assert "python" in parsed["skills"]

    match_payload = {
        "candidate_skills": ["python", "pytorch"],
        "candidate_experience_years": 4.0,
        "job_parsed": parsed
    }
    match_resp = client.post("/api/v1/jobs/match", json=match_payload)
    assert match_resp.status_code == 200
    assert match_resp.json()["overall_match"] > 70.0


def test_application_crm_api(client):
    app_payload = {
        "company_name": "Anthropic",
        "job_title": "AI Researcher",
        "status": "Saved"
    }
    create_resp = client.post("/api/v1/applications", json=app_payload)
    assert create_resp.status_code == 200
    app_data = create_resp.json()
    assert app_data["company_name"] == "Anthropic"

    kanban_resp = client.get("/api/v1/applications/kanban")
    assert kanban_resp.status_code == 200
    assert "Saved" in kanban_resp.json()


def test_next_best_action_api(client):
    resp = client.get("/api/v1/next-best-action")
    assert resp.status_code == 200
    actions = resp.json()["actions"]
    assert len(actions) > 0
