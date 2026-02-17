"""Token usage estimation and formatting utilities for pipelines."""

from __future__ import annotations

from config.pricing import MODEL_PRICING, estimate_cost


def estimate_pipeline_cost(
    model: str, input_tokens: int, output_tokens: int
) -> float:
    """Return estimated cost in USD for the given token counts."""
    return estimate_cost(model, input_tokens, output_tokens)


def format_token_summary(
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    model: str,
) -> str:
    """Return a human-readable summary of token usage and cost."""
    total = input_tokens + output_tokens
    return (
        f"{model}: {total:,} tokens "
        f"({input_tokens:,} in / {output_tokens:,} out) "
        f"${cost_usd:.4f}"
    )
