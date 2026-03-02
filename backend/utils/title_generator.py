"""LLM-based conversation title generator.

Generates concise 4-8 word titles from the first user/assistant exchange,
similar to ChatGPT's auto-generated conversation names.
"""

import logging
from backend.config.settings import settings
from backend.providers.factory import get_provider

logger = logging.getLogger(__name__)

# Models to try for title generation (cheapest first)
_TITLE_MODELS = [
    ("openai", "gpt-4.1-nano", "openai_api_key"),
    ("openai", "gpt-4o-mini", "openai_api_key"),
    ("google", "gemini-2.0-flash", "google_api_key"),
    ("groq", "meta-llama/llama-4-scout-17b-16e-instruct", "groq_api_key"),
    ("anthropic", "claude-haiku-4-5-20251001", "anthropic_api_key"),
]

_TITLE_SYSTEM_PROMPT = (
    "Generate a concise 4-8 word title for this conversation. "
    "The title should capture the main topic or question. "
    "Rules:\n"
    "- No quotes or quotation marks\n"
    "- No period at the end\n"
    "- No prefixes like 'Title:' or 'Topic:'\n"
    "- Just the title text, nothing else\n"
    "Examples: 'CRE Cap Rate Analysis', 'Python List Sorting Methods', "
    "'Bridge Loan Structure Comparison'"
)


def _auto_title_fallback(content: str) -> str:
    """Simple truncation fallback (same as original _auto_title)."""
    content = content.strip()
    if len(content) <= 50:
        return content
    truncated = content[:50]
    last_space = truncated.rfind(" ")
    if last_space > 20:
        truncated = truncated[:last_space]
    return truncated + "..."


def _clean_title(raw: str) -> str:
    """Clean LLM output to a proper title string."""
    title = raw.strip()
    # Remove surrounding quotes
    for q in ('"', "'", "\u201c", "\u201d", "\u2018", "\u2019"):
        title = title.strip(q)
    # Remove common prefixes
    for prefix in ("Title:", "Topic:", "Subject:"):
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):].strip()
    # Remove trailing punctuation
    title = title.rstrip(".!?")
    # Truncate to 60 chars at word boundary
    if len(title) > 60:
        truncated = title[:60]
        last_space = truncated.rfind(" ")
        if last_space > 20:
            title = truncated[:last_space]
        else:
            title = truncated
    return title or "New conversation"


async def generate_title(user_message: str, assistant_message: str) -> str:
    """Generate a conversation title using the cheapest available LLM.

    Args:
        user_message: First user message in the conversation.
        assistant_message: First assistant response.

    Returns:
        A concise 4-8 word title string.
    """
    user_content = (
        f"User: {user_message[:500]}\n"
        f"Assistant: {assistant_message[:500]}"
    )

    # Try each model until one works
    for provider_name, model_id, key_attr in _TITLE_MODELS:
        if not getattr(settings, key_attr, ""):
            continue  # API key not configured

        try:
            provider = get_provider(provider_name)
            response = await provider.send_message(
                messages=[{"role": "user", "content": user_content}],
                model=model_id,
                temperature=0.5,
                max_tokens=30,
                system_prompt=_TITLE_SYSTEM_PROMPT,
            )
            title = _clean_title(response.content)
            if title and title != "New conversation":
                logger.debug(
                    "Generated title '%s' using %s/%s (cost=$%.6f)",
                    title, provider_name, model_id, response.cost_usd,
                )
                return title
        except Exception as e:
            logger.debug("Title generation failed with %s/%s: %s", provider_name, model_id, e)
            continue

    # All models failed — fallback to simple truncation
    logger.warning("All title generation models failed, using truncation fallback")
    return _auto_title_fallback(user_message)
