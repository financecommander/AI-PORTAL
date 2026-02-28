"""Tests for email validation (Bug #5) and domain error message (Bug #4)."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.routes.auth import LoginRequest


# ─── Pydantic model tests (regex + normalisation) ───

class TestLoginRequestValidation:
    """Test the LoginRequest Pydantic model directly."""

    def test_valid_email(self):
        req = LoginRequest(email="user@example.com")
        assert req.email == "user@example.com"

    def test_email_normalised_to_lowercase(self):
        req = LoginRequest(email="USER@Example.COM")
        assert req.email == "user@example.com"

    def test_email_stripped(self):
        req = LoginRequest(email="  user@example.com  ")
        assert req.email == "user@example.com"

    def test_email_with_plus(self):
        req = LoginRequest(email="user+tag@example.com")
        assert req.email == "user+tag@example.com"

    def test_email_with_dots(self):
        req = LoginRequest(email="first.last@example.com")
        assert req.email == "first.last@example.com"

    def test_rejects_no_at_sign(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="notanemail")

    def test_rejects_no_domain(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="user@")

    def test_rejects_no_tld(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="user@localhost")

    def test_rejects_double_at(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="user@@example.com")

    def test_rejects_spaces_in_email(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="user @example.com")

    def test_rejects_empty_string(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="")

    def test_rejects_html_injection(self):
        with pytest.raises(ValidationError, match="Invalid email format"):
            LoginRequest(email="<script>@evil.com")


# ─── Route-level tests ───

def test_login_valid_domain_gradeesolutions(client: TestClient):
    """Allowed domain gradeesolutions.com returns a token."""
    resp = client.post("/auth/login", json={"email": "alice@gradeesolutions.com"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_valid_domain_calculusresearch(client: TestClient):
    """Allowed domain calculusresearch.io returns a token."""
    resp = client.post("/auth/login", json={"email": "bob@calculusresearch.io"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_domain_generic_error(client: TestClient):
    """Unauthorized domain returns 401 WITHOUT revealing the domain (Bug #4)."""
    resp = client.post("/auth/login", json={"email": "hacker@evil.com"})
    assert resp.status_code == 401
    detail = resp.json()["detail"]
    # Must not leak the attempted domain
    assert "evil.com" not in detail
    # Should still communicate what went wrong
    assert "not authorized" in detail.lower()


def test_login_malformed_email_returns_422(client: TestClient):
    """Malformed email rejected by Pydantic before hitting route logic."""
    resp = client.post("/auth/login", json={"email": "not-an-email"})
    assert resp.status_code == 422


def test_login_case_insensitive(client: TestClient):
    """Email matching is case-insensitive (validator lowercases)."""
    resp = client.post("/auth/login", json={"email": "Alice@GradeeSolutions.COM"})
    assert resp.status_code == 200
