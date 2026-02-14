"""FinanceCommander AI Portal - Streamlit Application Entry Point."""

import streamlit as st

from ui.sidebar import render_sidebar
from ui.chat_view import render_chat_view


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

    # Render UI components
    render_sidebar()
    render_chat_view()


if __name__ == "__main__":
    main()