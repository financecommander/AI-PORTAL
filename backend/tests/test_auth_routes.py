"""Test authentication routes."""

import pytest
from fastapi.testclient import TestClient


def test_login_valid_domain(client: TestClient):
    """Test valid login with @financecommander.com email."""
    response = client.post("/auth/login", json={"email": "test@financecommander.com"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_domain(client: TestClient):
    """Test login with unauthorized domain."""
    response = client.post("/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 401
    assert "not authorized" in response.json()["detail"].lower()


def test_login_missing_email(client: TestClient):
    """Test login with missing email field."""
    response = client.post("/auth/login", json={})
    assert response.status_code == 422


def test_verify_valid_token(client: TestClient, auth_headers: dict):
    """Test token verification with valid JWT."""
    # Assuming /auth/verify exists and returns 200 for valid token
    response = client.get("/auth/verify", headers=auth_headers)
    # If endpoint doesn't exist, this will fail, but per directive
    assert response.status_code == 200


def test_verify_expired_token(client: TestClient):
    """Test token verification with expired/invalid JWT."""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/auth/verify", headers=headers)
    assert response.status_code == 401


def test_verify_missing_header(client: TestClient):
    """Test token verification with missing Authorization header."""
    response = client.get("/auth/verify")
    assert response.status_code == 401