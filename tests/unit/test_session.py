"""Tests for session timeout functionality."""

import time
from unittest.mock import MagicMock, patch

import pytest

from auth.authenticator import AuthResult, authenticate, check_session_valid, logout
from config.settings import SESSION_TIMEOUT_SECONDS


@pytest.fixture
def mock_session_state():
    """Provide a dict that acts like st.session_state."""
    state = {
        "authenticated": True,
        "user_email": "user@financecommander.com",
        "portal_last_activity": time.time(),
    }
    with patch("auth.authenticator.st") as mock_st:
        mock_st.session_state = state
        yield state, mock_st


class TestSessionTimeout:
    def test_valid_session(self, mock_session_state):
        state, _ = mock_session_state
        assert check_session_valid() is True

    def test_expired_session(self, mock_session_state):
        state, _ = mock_session_state
        state["portal_last_activity"] = time.time() - SESSION_TIMEOUT_SECONDS - 1
        assert check_session_valid() is False

    def test_expired_clears_auth(self, mock_session_state):
        state, _ = mock_session_state
        state["portal_last_activity"] = time.time() - SESSION_TIMEOUT_SECONDS - 1
        check_session_valid()
        assert state["authenticated"] is False

    def test_no_timestamp_treated_as_expired(self, mock_session_state):
        state, _ = mock_session_state
        del state["portal_last_activity"]
        assert check_session_valid() is False

    def test_activity_refreshed_on_valid(self, mock_session_state):
        state, _ = mock_session_state
        old_ts = state["portal_last_activity"]
        time.sleep(0.01)
        check_session_valid()
        assert state["portal_last_activity"] > old_ts

    def test_unauthenticated_returns_false(self, mock_session_state):
        state, _ = mock_session_state
        state["authenticated"] = False
        assert check_session_valid() is False

    def test_timeout_constant_is_30_minutes(self):
        assert SESSION_TIMEOUT_SECONDS == 1800


class TestAuthenticate:
    def test_sets_last_activity(self):
        state = {}
        with patch("auth.authenticator.st") as mock_st:
            mock_st.session_state = state
            result = authenticate("user@financecommander.com")
        assert result.success is True
        assert "portal_last_activity" in state
        assert abs(state["portal_last_activity"] - time.time()) < 2

    def test_invalid_email(self):
        state = {}
        with patch("auth.authenticator.st") as mock_st:
            mock_st.session_state = state
            result = authenticate("bad")
        assert result.success is False

    def test_wrong_domain(self):
        state = {}
        with patch("auth.authenticator.st") as mock_st:
            mock_st.session_state = state
            result = authenticate("user@wrong.com")
        assert result.success is False

    def test_auth_result_fields(self):
        r = AuthResult(success=True, user_email="a@b.com")
        assert r.success is True
        assert r.user_email == "a@b.com"
        assert r.error_message is None


class TestLogout:
    def test_clears_auth_state(self):
        state = {
            "authenticated": True,
            "user_email": "u@financecommander.com",
            "portal_last_activity": time.time(),
            "portal_chat_history_x": [{"role": "user", "content": "hi"}],
        }
        with patch("auth.authenticator.st") as mock_st:
            mock_st.session_state = state
            logout()
        assert state["authenticated"] is False
        assert state["user_email"] == ""
        assert "portal_last_activity" not in state
        assert "portal_chat_history_x" not in state
