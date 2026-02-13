"""Per-model token pricing table.

Prices are in USD per 1K tokens: (input_price, output_price).
Last verified: 2025-01-15.
"""

MODEL_PRICING: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o": (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    # Anthropic
    "claude-3-opus": (0.015, 0.075),
    "claude-3-sonnet": (0.003, 0.015),
    "claude-3-haiku": (0.00025, 0.00125),
    # Google
    "gemini-1.5-pro": (0.00125, 0.005),
    "gemini-1.5-flash": (0.000075, 0.0003),
    # xAI / Grok
    "grok-2": (0.002, 0.01),
}


def estimate_cost(
    model: str, input_tokens: int, output_tokens: int
) -> float:
    """Return estimated cost in USD for the given token counts."""
    input_price, output_price = MODEL_PRICING.get(model, (0.0, 0.0))
    return (input_tokens / 1000) * input_price + (
        output_tokens / 1000
    ) * output_price
