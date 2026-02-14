"""FinanceCommander AI Portal - Streamlit Application Entry Point."""

import streamlit as st

from auth.authenticator import check_session_valid
from auth.rate_limiter import TokenBucket
from ui.chat_view import render_chat_view
from ui.sidebar import render_sidebar


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="FinanceCommander AI Portal",
        page_icon="💰",
        layout="wide",
    )

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "portal_rate_bucket" not in st.session_state:
        st.session_state["portal_rate_bucket"] = TokenBucket()

    # Session timeout check
    if st.session_state.get("authenticated", False):
        if not check_session_valid():
            st.warning("⏰ Session expired due to inactivity. Please log in again.")

    # Render UI components
    render_sidebar()
    render_chat_view()


if __name__ == "__main__":
    main()