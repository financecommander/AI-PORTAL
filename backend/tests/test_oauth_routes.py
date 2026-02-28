"""Tests for OAuth authorization routes."""

import pytest
from fastapi.testclient import TestClient


def test_oauth_authorize_unknown_provider(client: TestClient):
    """Unknown OAuth provider returns 404."""
    response = client.get("/auth/oauth/github/authorize", follow_redirects=False)
    assert response.status_code == 404


def test_oauth_authorize_unconfigured_provider(client: TestClient, monkeypatch):
    """Configured provider with empty credentials returns 503."""
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "")
    # Re-import settings so the patch takes effect in the route
    response = client.get("/auth/oauth/google/authorize", follow_redirects=False)
    assert response.status_code == 503


def test_oauth_authorize_google_redirects(client: TestClient, monkeypatch):
    """Google authorize endpoint redirects when credentials are set."""
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test-google-client-id")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "test-google-secret")
    from backend.config import settings as _settings_mod
    _settings_mod.settings.google_oauth_client_id = "test-google-client-id"
    _settings_mod.settings.google_oauth_client_secret = "test-google-secret"

    response = client.get("/auth/oauth/google/authorize", follow_redirects=False)
    assert response.status_code in (302, 307)
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(response.headers["location"])
    assert parsed.netloc == "accounts.google.com"
    assert "test-google-client-id" in response.headers["location"]
    assert "state=" in response.headers["location"]


def test_oauth_authorize_x_redirects(client: TestClient, monkeypatch):
    """X authorize endpoint redirects when credentials are set."""
    from backend.config import settings as _settings_mod
    _settings_mod.settings.x_oauth_client_id = "test-x-client-id"
    _settings_mod.settings.x_oauth_client_secret = "test-x-secret"

    response = client.get("/auth/oauth/x/authorize", follow_redirects=False)
    assert response.status_code in (302, 307)
    from urllib.parse import urlparse
    assert urlparse(response.headers["location"]).netloc == "twitter.com"


def test_oauth_authorize_apple_redirects(client: TestClient, monkeypatch):
    """Apple authorize endpoint redirects when credentials are set."""
    from backend.config import settings as _settings_mod
    _settings_mod.settings.apple_oauth_client_id = "test-apple-client-id"
    _settings_mod.settings.apple_oauth_client_secret = "test-apple-secret"

    response = client.get("/auth/oauth/apple/authorize", follow_redirects=False)
    assert response.status_code in (302, 307)
    from urllib.parse import urlparse
    assert urlparse(response.headers["location"]).netloc == "appleid.apple.com"
    # Apple requires form_post
    assert "form_post" in response.headers["location"]


def test_oauth_callback_unknown_provider(client: TestClient):
    """Unknown provider in callback returns 404."""
    response = client.get(
        "/auth/oauth/github/callback?code=abc&state=x:1:sig",
        follow_redirects=False,
    )
    assert response.status_code == 404


def test_oauth_callback_invalid_state(client: TestClient):
    """Callback with invalid state returns 400."""
    response = client.get(
        "/auth/oauth/google/callback?code=abc&state=bad-state",
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "state" in response.json()["detail"].lower()


def test_oauth_callback_provider_error_redirects(client: TestClient):
    """Callback with error param from provider redirects to frontend error page."""
    # Build a valid state so we pass state check (provider error is checked first)
    response = client.get(
        "/auth/oauth/google/callback?code=abc&state=x&error=access_denied",
        follow_redirects=False,
    )
    # Should redirect to frontend with error param
    assert response.status_code in (302, 307)
    assert "error=access_denied" in response.headers["location"]


def test_oauth_state_helpers():
    """_make_state produces a state that _verify_state accepts."""
    from backend.routes.oauth import _make_state, _verify_state

    state = _make_state("google")
    assert _verify_state("google", state) is True
    # Wrong provider
    assert _verify_state("x", state) is False
    # Tampered sig
    assert _verify_state("google", state + "x") is False
    # Empty
    assert _verify_state("google", "") is False
