"""
Unit tests for ResumeIQ Authentication & JWT system.
"""

import pytest
from backend.api.auth_routes import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    password = "SuperSecretPassword123!"
    pw_hash = hash_password(password)
    assert pw_hash != password
    assert verify_password(password, pw_hash)
    assert not verify_password("WrongPassword", pw_hash)


def test_jwt_token_flow():
    user_id = 42
    email = "testcandidate@resumeiq.ai"
    role = "candidate"

    token = create_access_token(user_id, email, role)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["email"] == email
    assert payload["role"] == role


def test_invalid_jwt_token():
    assert decode_access_token("invalid.token.str") is None
    assert decode_access_token("bogus") is None


def test_signup_and_login_api(client):
    # Test Signup
    signup_payload = {
        "email": "user@example.com",
        "password": "Password123",
        "full_name": "Test User",
        "target_role": "Data Scientist"
    }
    resp = client.post("/api/v1/auth/signup", json=signup_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "user@example.com"
    assert data["profile"]["full_name"] == "Test User"

    # Test Duplicate Signup
    resp_dup = client.post("/api/v1/auth/signup", json=signup_payload)
    assert resp_dup.status_code == 400

    # Test Login
    login_payload = {"email": "user@example.com", "password": "Password123"}
    resp_login = client.post("/api/v1/auth/login", json=login_payload)
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]

    # Test Me endpoint with bearer token
    resp_me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_me.status_code == 200
    assert resp_me.json()["user"]["email"] == "user@example.com"
