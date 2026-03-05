"""Conversation history summarizer for context window management.

When conversation history exceeds ~70% of the model's context window,
older messages are compressed into a system-level summary while keeping
recent messages intact. This prevents token overflow errors while
preserving essential context.
"""

import logging
from typing import Optional

from backend.config.settings import settings
from backend.providers.factory import get_provider
from pricing import estimate_tokens, MODEL_CONTEXT_WINDOWS

logger = logging.getLogger(__name__)

# Threshold: summarize when history exceeds this fraction of context window
SUMMARIZE_THRESHOLD = 0.70

# Keep recent messages filling up to this fraction of context for direct use
RECENT_BUDGET_FRACTION = 0.30

# Models to try for summarization (cheapest/fastest first)
_SUMMARIZER_MODELS = [
    ("openai", "gpt-4.1-nano", "openai_api_key"),
    ("openai", "gpt-4o-mini", "openai_api_key"),
    ("google", "gemini-2.0-flash", "google_api_key"),
    ("groq", "meta-llama/llama-4-scout-17b-16e-instruct", "groq_api_key"),
    ("anthropic", "claude-haiku-4-5-20251001", "anthropic_api_key"),
]

_SUMMARIZER_SYSTEM_PROMPT = (
    "You are a conversation summarizer. Produce a concise summary of the "
    "conversation below, preserving:\n"
    "- Key facts, numbers, and decisions\n"
    "- Important context and constraints mentioned\n"
    "- The user's goals and preferences\n"
    "- Any action items or conclusions\n\n"
    "Write in third person. Be thorough but concise. "
    "Do NOT add new information or opinions."
)


def _estimate_messages_tokens(messages: list[dict]) -> int:
    """Estimate total tokens for a list of messages."""
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            # Multipart content (attachments)
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    total += estimate_tokens(part["text"])
        # Add overhead per message (role, formatting)
        total += 4
    return total


async def _call_summarizer(conversation_text: str) -> Optional[str]:
    """Call a cheap LLM to summarize conversation text."""
    for provider_name, model_id, key_attr in _SUMMARIZER_MODELS:
        if not getattr(settings, key_attr, ""):
            continue

        try:
            provider = get_provider(provider_name)
            response = await provider.send_message(
                messages=[{"role": "user", "content": conversation_text}],
                model=model_id,
                temperature=0.3,
                max_tokens=1000,
                system_prompt=_SUMMARIZER_SYSTEM_PROMPT,
            )
            if response.content.strip():
                logger.info(
                    "Summarized conversation using %s/%s (%d input → %d output tokens, $%.6f)",
                    provider_name, model_id,
                    response.input_tokens, response.output_tokens, response.cost_usd,
                )
                return response.content.strip()
        except Exception as e:
            logger.debug("Summarization failed with %s/%s: %s", provider_name, model_id, e)
            continue

    return None


async def summarize_history(
    messages: list[dict],
    model: str,
    context_window: Optional[int] = None,
) -> tuple[list[dict], bool]:
    """Compress conversation history if it exceeds the context window threshold.

    Args:
        messages: Full message list (role/content dicts) to send to the LLM.
        model: Model ID being used (for context window lookup).
        context_window: Override context window size (tokens). If None, looked up.

    Returns:
        Tuple of (compressed_messages, was_summarized).
        If under threshold, returns original messages unchanged with False.
    """
    if not messages or len(messages) <= 4:
        return messages, False

    # Get context window for this model
    if context_window is None:
        context_window = MODEL_CONTEXT_WINDOWS.get(model, 128_000)

    threshold = int(context_window * SUMMARIZE_THRESHOLD)
    total_tokens = _estimate_messages_tokens(messages)

    if total_tokens <= threshold:
        return messages, False

    logger.info(
        "History exceeds threshold: ~%d tokens vs %d limit (%d%% of %d context). "
        "Summarizing older messages for model '%s'.",
        total_tokens, threshold,
        int(total_tokens / context_window * 100), context_window, model,
    )

    # Determine how many recent messages to keep
    recent_budget = int(context_window * RECENT_BUDGET_FRACTION)
    recent_messages: list[dict] = []
    recent_tokens = 0

    # Walk backward from the end, keeping messages that fit in the budget
    for msg in reversed(messages):
        msg_tokens = estimate_tokens(msg.get("content", "")) + 4
        if recent_tokens + msg_tokens > recent_budget and recent_messages:
            break
        recent_messages.insert(0, msg)
        recent_tokens += msg_tokens

    # Always keep at least the last 2 messages (current exchange)
    if len(recent_messages) < 2 and len(messages) >= 2:
        recent_messages = messages[-2:]

    # Messages to summarize = everything not in recent
    older_count = len(messages) - len(recent_messages)
    if older_count <= 1:
        # Not enough to summarize — send as-is
        return messages, False

    older_messages = messages[:older_count]

    # Build conversation text for summarization
    conv_lines = []
    for msg in older_messages:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        if isinstance(content, list):
            # Extract text from multipart
            content = " ".join(
                p.get("text", "") for p in content if isinstance(p, dict)
            )
        conv_lines.append(f"{role}: {content[:1000]}")

    conversation_text = "\n\n".join(conv_lines)

    # Truncate if the text to summarize is itself very long
    max_summarize_chars = 30000  # ~7500 tokens
    if len(conversation_text) > max_summarize_chars:
        conversation_text = conversation_text[:max_summarize_chars] + "\n\n[...truncated]"

    summary = await _call_summarizer(conversation_text)

    if not summary:
        # Summarization failed — send as-is (may cause token overflow)
        logger.warning("Summarization failed, sending full history")
        return messages, False

    # Build compressed message list
    summary_msg = {
        "role": "system",
        "content": (
            f"Summary of the earlier conversation ({older_count} messages):\n\n"
            f"{summary}"
        ),
    }

    compressed = [summary_msg] + recent_messages
    compressed_tokens = _estimate_messages_tokens(compressed)

    logger.info(
        "Compressed %d messages (%d→%d tokens): "
        "summarized %d older + kept %d recent",
        len(messages), total_tokens, compressed_tokens,
        older_count, len(recent_messages),
    )

    return compressed, True
