"""Authentication module for FinanceCommander AI Portal."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import streamlit as st

from config.settings import ALLOWED_DOMAINS, SESSION_TIMEOUT_SECONDS


@dataclass
class AuthResult:
    """Result of authentication attempt."""
    success: bool
    user_email: Optional[str] = None
    error_message: Optional[str] = None


def authenticate(email: str) -> AuthResult:
    """Authenticate user by email domain.

    Args:
        email: User's email address

    Returns:
        AuthResult with success status and user info
    """
    if not email or "@" not in email:
        return AuthResult(success=False, error_message="Invalid email format")

    domain = email.split("@")[1].lower()

    if domain not in ALLOWED_DOMAINS:
        return AuthResult(
            success=False,
            error_message=f"Access denied. Only {', '.join(ALLOWED_DOMAINS)} domains allowed."
        )

    # Set activity timestamp on successful auth
    st.session_state["portal_last_activity"] = time.time()
    return AuthResult(success=True, user_email=email)


def get_current_user() -> Optional[str]:
    """Get currently authenticated user email from session state."""
    if st.session_state.get("authenticated", False):
        return st.session_state.get("user_email")
    return None


def check_session_valid() -> bool:
    """Check if the current session is still valid (not timed out).

    Returns True if session is valid, False if expired.
    Also updates the last-activity timestamp when valid.
    """
    if not st.session_state.get("authenticated", False):
        return False

    last_activity = st.session_state.get("portal_last_activity")
    if last_activity is None:
        # No timestamp recorded — treat as expired
        return False

    elapsed = time.time() - last_activity
    if elapsed > SESSION_TIMEOUT_SECONDS:
        logout()
        return False

    # Refresh activity timestamp
    st.session_state["portal_last_activity"] = time.time()
    return True


def logout():
    """Clear authentication session."""
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = ""
    # Remove portal-specific keys
    keys_to_clear = [k for k in st.session_state if k.startswith("portal_")]
    for k in keys_to_clear:
        del st.session_state[k]