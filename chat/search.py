"""Conversation search for chat history.

Provides case-insensitive substring search across chat history
with results ranked by recency.
"""

from __future__ import annotations


def search_history(
    history: list[dict],
    query: str,
    max_results: int = 10,
) -> list[dict]:
    """Search chat history for messages containing the query.

    Uses case-insensitive substring matching with result ranking
    by recency. Returns message dicts with an added ``match_index``
    field indicating the original position in *history*.

    Args:
        history: List of message dicts with ``role`` and ``content`` keys.
        query: Search string to match against message content.
        max_results: Maximum number of results to return.

    Returns:
        List of matching message dicts (most recent first), each
        augmented with a ``match_index`` key.
    """
    if not query or not query.strip():
        return []

    query_lower = query.lower()
    results: list[dict] = []

    for i, msg in enumerate(reversed(history)):
        content = msg.get("content", "")
        if query_lower in content.lower():
            results.append({**msg, "match_index": len(history) - 1 - i})
            if len(results) >= max_results:
                break

    return results
