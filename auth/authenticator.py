"""Authentication module for FinanceCommander AI Portal."""

from dataclasses import dataclass
from typing import Optional

import streamlit as st

from config.settings import ALLOWED_DOMAINS


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

    return AuthResult(success=True, user_email=email)


def get_current_user() -> Optional[str]:
    """Get currently authenticated user email from session state."""
    if st.session_state.get("authenticated", False):
        return st.session_state.get("user_email")
    return None


def logout():
    """Clear authentication session."""
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.clear()  # Clear all session state