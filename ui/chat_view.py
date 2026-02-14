"""Chat view UI component for FinanceCommander AI Portal."""

from __future__ import annotations

import asyncio
import sys
import time

import streamlit as st

from chat.engine import ChatEngine, Message
from chat.logger import UsageLogger
from config.settings import MAX_CHAT_HISTORY, STREAMING_ENABLED
from providers import get_provider


def _history_key(specialist_id: str) -> str:
    return f"portal_chat_history_{specialist_id}"


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

    hk = _history_key(specialist.id)
    if hk not in st.session_state:
        st.session_state[hk] = []

    # Render existing messages
    for message in st.session_state[hk]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Rate-limit check
        bucket = st.session_state.get("portal_rate_bucket")
        if bucket is not None and not bucket.consume():
            st.error(
                f"⏳ Rate limit exceeded. Try again in {bucket.retry_after_seconds}s."
            )
            return

        # Append user message
        st.session_state[hk].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build engine
        engine = _build_engine(specialist, st.session_state[hk])

        # Generate response
        with st.chat_message("assistant"):
            if STREAMING_ENABLED:
                response_text = _handle_streaming(engine, specialist)
            else:
                response_text = _handle_non_streaming(engine)

        if response_text is not None:
            st.session_state[hk].append(
                {"role": "assistant", "content": response_text}
            )
            # Trim history
            if len(st.session_state[hk]) > MAX_CHAT_HISTORY * 2:
                st.session_state[hk] = st.session_state[hk][
                    -(MAX_CHAT_HISTORY * 2) :
                ]


def _build_engine(specialist, history: list[dict]) -> ChatEngine:
    """Construct a ChatEngine with the current history replayed."""
    user_email = st.session_state.get("user_email", "")
    base_url = getattr(specialist, "base_url", "") or ""
    provider = get_provider(specialist.provider, base_url=base_url)
    logger = UsageLogger()
    engine = ChatEngine(
        provider=provider,
        specialist=specialist,
        logger=logger,
        user_email=user_email,
    )
    # Replay all stored messages (engine already has system prompt)
    for msg in history:
        engine.history.append(Message(role=msg["role"], content=msg["content"]))
    return engine


def _handle_streaming(engine: ChatEngine, specialist) -> str | None:
    """Stream response with placeholder + markdown cursor. Falls back on error."""
    try:
        placeholder = st.empty()
        full_response = ""

        # Remove the last user message since send_streaming will re-add it
        last_user_content = engine.history[-1].content
        engine.history.pop()

        async def _stream():
            nonlocal full_response
            async for chunk in engine.send_streaming(last_user_content):
                if not chunk.is_final:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")

        asyncio.run(_stream())
        placeholder.markdown(full_response)
        engine.append_assistant_message(full_response)
        return full_response

    except Exception as e:
        print(
            f"Streaming failed ({specialist.provider}), falling back: {e}",
            file=sys.stderr,
        )
        return _handle_non_streaming(engine)


def _handle_non_streaming(engine: ChatEngine) -> str | None:
    """Non-streaming response with spinner."""
    with st.spinner("Thinking..."):
        try:
            if engine.history and engine.history[-1].role == "user":
                last_user_content = engine.history[-1].content
                engine.history.pop()
                response = asyncio.run(engine.send(last_user_content))
            else:
                response = asyncio.run(engine.send(""))
            st.markdown(response)
            return response
        except Exception as e:
            st.error(f"Error: {e}")
            return None