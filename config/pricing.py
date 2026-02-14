"""Per-model token pricing table.

Prices are in USD per 1M tokens: (input_price, output_price).
Last verified: 2025-01-15.
"""

MODEL_PRICING: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    # Anthropic
    "claude-3-opus": (15.00, 75.00),
    "claude-3-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),
    # Google
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    # xAI / Grok
    "grok-2": (2.00, 10.00),
}


def estimate_cost(
    model: str, input_tokens: int, output_tokens: int
) -> float:
    """Return estimated cost in USD for the given token counts."""
    input_price, output_price = MODEL_PRICING.get(model, (0.0, 0.0))
    return (input_tokens / 1_000_000) * input_price + (
        output_tokens / 1_000_000
    ) * output_price
