"""Sidebar UI component for FinanceCommander AI Portal."""

import streamlit as st

from auth.authenticator import authenticate, get_current_user, logout
from specialists.manager import SpecialistManager


def render_sidebar():
    """Render the sidebar with authentication and specialist selection."""
    with st.sidebar:
        st.title("💰 FinanceCommander AI")

        # Authentication section
        if not st.session_state.get("authenticated", False):
            _render_auth_form()
        else:
            _render_user_info()

        # Specialist selection
        if st.session_state.get("authenticated", False):
            _render_specialist_selector()


def _render_auth_form():
    """Render authentication form."""
    st.subheader("🔐 Authentication")

    with st.form("auth_form"):
        email = st.text_input("Email address", placeholder="user@financecommander.com")
        submitted = st.form_submit_button("Authenticate")

        if submitted:
            result = authenticate(email)
            if result.success:
                st.session_state.authenticated = True
                st.session_state.user_email = result.user_email
                st.success(f"Welcome, {result.user_email}!")
                st.rerun()
            else:
                st.error(result.error_message)


def _render_user_info():
    """Render authenticated user info and logout."""
    user_email = get_current_user()
    if user_email:
        st.subheader("👤 User")
        st.write(f"**{user_email}**")

        if st.button("Logout"):
            logout()
            st.rerun()


def _render_specialist_selector():
    """Render specialist selection dropdown."""
    st.subheader("🎯 Specialist")

    manager = SpecialistManager()
    specialists = manager.list()

    if specialists:
        specialist_names = [s.name for s in specialists]
        selected_name = st.selectbox(
            "Choose a specialist:",
            specialist_names,
            key="selected_specialist"
        )

        # Store selected specialist in session state
        selected_specialist = next(
            (s for s in specialists if s.name == selected_name), None
        )
        st.session_state.selected_specialist = selected_specialist

        if selected_specialist:
            st.caption(f"**{selected_specialist.name}**")
            st.caption(selected_specialist.description)
    else:
        st.warning("No specialists available")