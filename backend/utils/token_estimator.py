"""Token estimation and cost calculation for LLM providers."""

from typing import Optional


# Pricing per 1M tokens (USD)
MODEL_PRICING = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-5.3-codex": (10.00, 40.00),  # TODO: verify model string
    "o1": (15.00, 60.00),
    "o1-mini": (3.00, 12.00),
    "o3-mini": (1.00, 4.00),
    # Anthropic
    "claude-opus-4": (15.00, 75.00),
    "claude-opus-4-6": (15.00, 75.00),  # TODO: verify model string
    "claude-sonnet-4": (3.00, 15.00),
    "claude-haiku-4": (0.25, 1.25),
    # Google
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-3-pro": (1.00, 4.00),  # TODO: verify model string
    # xAI
    "grok-3": (5.00, 15.00),
    "grok-4-1-fast-reasoning": (5.00, 15.00),  # TODO: verify model string
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost for token usage.
    
    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Cost in USD
    """
    if model not in MODEL_PRICING:
        # Default to mid-tier pricing for unknown models
        return (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000
    
    input_price, output_price = MODEL_PRICING[model]
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    Simple approximation: 1 token ≈ 4 characters
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def get_model_pricing(model: str) -> Optional[tuple[float, float]]:
    """
    Get pricing for a specific model.
    
    Args:
        model: Model name
    
    Returns:
        Tuple of (input_price_per_1m, output_price_per_1m) or None
    """
    return MODEL_PRICING.get(model)
