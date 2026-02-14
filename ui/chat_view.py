"""Chat view UI component for FinanceCommander AI Portal."""

import asyncio
import time

import streamlit as st

from chat.engine import ChatEngine
from chat.logger import UsageLogger
from providers import get_provider


def render_chat_view():
    """Render the main chat interface."""
    st.title("💬 AI Chat Portal")

    if not st.session_state.get("authenticated", False):
        st.info("Please authenticate using the sidebar to start chatting.")
        return

    specialist = st.session_state.get("selected_specialist")
    if not specialist:
        st.info("Please select a specialist from the sidebar.")
        return

    user_email = st.session_state.get("user_email", "")

    # Initialize chat engine
    provider = get_provider(specialist.provider)
    logger = UsageLogger()
    engine = ChatEngine(
        provider=provider,
        specialist=specialist,
        logger=logger,
        user_email=user_email
    )

    # Chat interface
    _render_chat_messages()
    _render_chat_input(engine)


def _render_chat_messages():
    """Render chat message history."""
    for message in st.session_state.get("chat_history", []):
        with st.chat_message(message["role"]):
            st.write(message["content"])


def _render_chat_input(engine: ChatEngine):
    """Render chat input and handle responses."""
    if prompt := st.chat_input("Type your message..."):
        # Add user message to history
        st.session_state.setdefault("chat_history", []).append({
            "role": "user",
            "content": prompt
        })

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    start_time = time.time()
                    response = asyncio.run(engine.send(prompt))
                    latency = time.time() - start_time

                    st.write(response)

                    # Add assistant message to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    # Log error if logger available
                    if hasattr(engine, 'logger') and engine.logger:
                        # Note: In a real implementation, you'd log the error
                        pass