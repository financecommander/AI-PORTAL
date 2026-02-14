"""Chat view UI component for FinanceCommander AI Portal."""

from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime, timezone

import streamlit as st

from chat.engine import ChatEngine, Message
from chat.file_handler import ALLOWED_EXTENSIONS, ChatAttachment, process_upload
from chat.logger import UsageLogger
from chat.search import search_history
from config.pricing import estimate_cost
from config.settings import MAX_CHAT_HISTORY, STREAMING_ENABLED
from portal.errors import ValidationError
from providers import get_provider


def _history_key(specialist_id: str) -> str:
    return f"portal_chat_history_{specialist_id}"


def _timestamps_key(specialist_id: str) -> str:
    return f"portal_chat_timestamps_{specialist_id}"


def _token_info_key(specialist_id: str) -> str:
    return f"portal_chat_token_info_{specialist_id}"


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
    tk = _timestamps_key(specialist.id)
    ik = _token_info_key(specialist.id)

    if hk not in st.session_state:
        st.session_state[hk] = []
    if tk not in st.session_state:
        st.session_state[tk] = []
    if ik not in st.session_state:
        st.session_state[ik] = []

    # -- Search bar --
    search_query = st.text_input(
        "🔍 Search conversation",
        key=f"portal_search_{specialist.id}",
        placeholder="Search messages...",
        label_visibility="collapsed",
    )

    if search_query:
        results = search_history(st.session_state[hk], search_query)
        if results:
            st.caption(f"Found {len(results)} match{'es' if len(results) != 1 else ''}")
            for r in results:
                with st.chat_message(r["role"]):
                    st.markdown(r["content"])
        else:
            st.caption("No matches found")
        return  # Show search results instead of full history

    # -- Chat history --
    history = st.session_state[hk]
    timestamps = st.session_state[tk]
    token_info = st.session_state[ik]

    for idx, message in enumerate(history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Timestamp
            if idx < len(timestamps) and timestamps[idx]:
                _show_relative_time(timestamps[idx])
            # Token info for assistant messages
            if (
                message["role"] == "assistant"
                and idx < len(token_info)
                and token_info[idx]
            ):
                info = token_info[idx]
                st.caption(
                    f"📊 {info['input_tokens']} in / {info['output_tokens']} out · "
                    f"${info['cost']:.4f} · {info['latency_ms']:.0f}ms"
                )

    # -- Regenerate button --
    if history and history[-1].get("role") == "assistant" and len(history) >= 2:
        if st.button("🔄 Regenerate response", key=f"portal_regen_{specialist.id}"):
            _regenerate(specialist, hk, tk, ik)
            st.rerun()

    # -- File upload --
    uploaded_file = st.file_uploader(
        "Attach a file",
        type=list(ext.lstrip(".") for ext in ALLOWED_EXTENSIONS),
        key=f"portal_file_upload_{specialist.id}",
        label_visibility="collapsed",
    )

    attachment: ChatAttachment | None = None
    if uploaded_file:
        try:
            attachment = process_upload(uploaded_file)
            st.caption(f"📎 {attachment.filename} ({attachment.size_bytes / 1024:.1f} KB)")
        except ValidationError as e:
            st.error(str(e))
            attachment = None

    # -- Chat input --
    if prompt := st.chat_input("Type your message..."):
        bucket = st.session_state.get("portal_rate_bucket")
        if bucket is not None and not bucket.consume():
            st.error(
                f"⏳ Rate limit exceeded. Try again in {bucket.retry_after_seconds}s."
            )
            return

        # Build display message (with attachment note if any)
        display_prompt = prompt
        if attachment:
            display_prompt = f"📎 *{attachment.filename}*\n\n{prompt}"

        st.session_state[hk].append({"role": "user", "content": display_prompt})
        st.session_state[tk].append(datetime.now(timezone.utc).isoformat())
        st.session_state[ik].append(None)

        with st.chat_message("user"):
            st.markdown(display_prompt)

        engine = _build_engine(specialist, st.session_state[hk])

        with st.chat_message("assistant"):
            if STREAMING_ENABLED:
                response_text, resp_info = _handle_streaming(engine, specialist)
            else:
                response_text, resp_info = _handle_non_streaming(engine)

        if response_text is not None:
            st.session_state[hk].append(
                {"role": "assistant", "content": response_text}
            )
            st.session_state[tk].append(datetime.now(timezone.utc).isoformat())
            st.session_state[ik].append(resp_info)
            if len(st.session_state[hk]) > MAX_CHAT_HISTORY * 2:
                st.session_state[hk] = st.session_state[hk][-(MAX_CHAT_HISTORY * 2):]
                st.session_state[tk] = st.session_state[tk][-(MAX_CHAT_HISTORY * 2):]
                st.session_state[ik] = st.session_state[ik][-(MAX_CHAT_HISTORY * 2):]


def _show_relative_time(iso_ts: str) -> None:
    """Display a relative timestamp caption."""
    try:
        ts = datetime.fromisoformat(iso_ts)
        now = datetime.now(timezone.utc)
        delta = now - ts
        seconds = int(delta.total_seconds())
        if seconds < 60:
            label = "just now"
        elif seconds < 3600:
            mins = seconds // 60
            label = f"{mins} min ago"
        elif seconds < 86400:
            hrs = seconds // 3600
            label = f"{hrs}h ago"
        else:
            days = seconds // 86400
            label = f"{days}d ago"
        st.caption(f"🕐 {label}")
    except (ValueError, TypeError):
        pass


def _regenerate(specialist, hk: str, tk: str, ik: str) -> None:
    """Remove last assistant response and re-send the last user message."""
    history = st.session_state[hk]
    timestamps = st.session_state[tk]
    token_info = st.session_state[ik]

    # Pop assistant message
    if history and history[-1]["role"] == "assistant":
        history.pop()
        if timestamps:
            timestamps.pop()
        if token_info:
            token_info.pop()

    # Pop user message — we'll re-send it
    if history and history[-1]["role"] == "user":
        last_user_msg = history.pop()
        if timestamps:
            timestamps.pop()
        if token_info:
            token_info.pop()

        # Re-add user message with fresh timestamp
        history.append(last_user_msg)
        timestamps.append(datetime.now(timezone.utc).isoformat())
        token_info.append(None)

        engine = _build_engine(specialist, history)
        if STREAMING_ENABLED:
            response_text, resp_info = _handle_streaming(engine, specialist)
        else:
            response_text, resp_info = _handle_non_streaming(engine)

        if response_text is not None:
            history.append({"role": "assistant", "content": response_text})
            timestamps.append(datetime.now(timezone.utc).isoformat())
            token_info.append(resp_info)


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
    for msg in history:
        engine.history.append(Message(role=msg["role"], content=msg["content"]))
    return engine


def _handle_streaming(
    engine: ChatEngine,
    specialist,
    attachment: ChatAttachment | None = None,
) -> tuple[str | None, dict | None]:
    """Stream response with placeholder + markdown cursor."""
    try:
        placeholder = st.empty()
        full_response = ""
        resp_info: dict | None = None

        last_user_content = engine.history[-1].content
        engine.history.pop()

        async def _stream():
            nonlocal full_response, resp_info
            async for chunk in engine.send_streaming(last_user_content):
                if chunk.is_final:
                    cost = estimate_cost(
                        chunk.model, chunk.input_tokens, chunk.output_tokens
                    )
                    resp_info = {
                        "input_tokens": chunk.input_tokens,
                        "output_tokens": chunk.output_tokens,
                        "cost": cost,
                        "latency_ms": chunk.latency_ms,
                    }
                else:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")

        asyncio.run(_stream())
        placeholder.markdown(full_response)
        engine.append_assistant_message(full_response)
        return full_response, resp_info

    except Exception as e:
        print(
            f"Streaming failed ({specialist.provider}), falling back: {e}",
            file=sys.stderr,
        )
        return _handle_non_streaming(engine)


def _handle_non_streaming(
    engine: ChatEngine,
    attachment: ChatAttachment | None = None,
) -> tuple[str | None, dict | None]:
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
            return response, None
        except Exception as e:
            st.error(f"Error: {e}")
            return None, None
            return None