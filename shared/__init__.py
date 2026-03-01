"""Shared pricing and token estimation for all AI Portal applications.

This module provides unified pricing data and cost calculation functions
used by both the Streamlit frontend and FastAPI backend.

Prices are in USD per 1M tokens: (input_price, output_price).
Last verified: 2026-02-28.
"""

from typing import Optional


# Comprehensive model pricing table
MODEL_PRICING: dict[str, tuple[float, float]] = {
    # OpenAI — GPT-5 series (current flagships)
    "gpt-5.2": (1.75, 14.00),
    "gpt-5.2-pro": (21.00, 168.00),
    "gpt-5": (1.25, 10.00),
    "gpt-5-nano": (0.05, 0.40),

    # OpenAI — GPT-4.1 series (still on API, retired from ChatGPT Feb 13)
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),

    # OpenAI — Reasoning / Legacy
    "o3-mini": (1.10, 4.40),
    "o3": (2.00, 8.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "o1": (15.00, 60.00),
    "o1-mini": (3.00, 12.00),

    # Anthropic — Claude 4.6 series (Feb 2026, latest)
    "claude-opus-4-6": (5.00, 25.00),
    "claude-sonnet-4-6": (3.00, 15.00),

    # Anthropic — Claude 4.5 series
    "claude-opus-4-5": (5.00, 25.00),
    "claude-sonnet-4-5-20250929": (3.00, 15.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-haiku-4-5": (1.00, 5.00),

    # Anthropic — Legacy
    "claude-opus-4": (15.00, 75.00),
    "claude-opus-4-20250514": (15.00, 75.00),
    "claude-sonnet-4": (3.00, 15.00),
    "claude-haiku-4": (0.25, 1.25),
    "claude-3-opus": (15.00, 75.00),
    "claude-3-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),

    # Google — Gemini 3 series (Jan/Feb 2026, latest)
    "gemini-3.1-pro-preview": (1.25, 10.00),
    "gemini-3-pro-preview": (2.00, 12.00),
    "gemini-3-flash-preview": (0.50, 3.00),

    # Google — Gemini 2.5 series
    "gemini-2.5-flash": (0.15, 0.60),
    "gemini-2.5-pro": (1.25, 10.00),

    # Google — Gemini 2.0 / Legacy
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-2.0-flash-exp": (0.10, 0.40),
    "gemini-2.0-pro": (1.25, 10.00),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),

    # xAI / Grok — Grok 4 series (current flagships)
    "grok-4": (3.00, 15.00),
    "grok-4-fast-reasoning": (0.20, 0.50),
    "grok-4-fast-non-reasoning": (0.20, 0.50),
    "grok-4-1-fast": (0.20, 0.50),
    "grok-4-1-fast-reasoning": (0.20, 0.50),
    "grok-4-1-fast-non-reasoning": (0.20, 0.50),

    # xAI / Grok — Legacy
    "grok-3": (3.00, 15.00),
    "grok-3-mini-beta": (0.30, 0.50),
    "grok-3-mini": (0.30, 0.50),
    "grok-beta": (5.00, 15.00),
    "grok-2": (2.00, 10.00),

    # DeepSeek (OpenAI-compatible API)
    "deepseek-reasoner": (0.55, 2.19),
    "deepseek-chat": (0.27, 0.41),
    "deepseek-r1": (0.55, 2.19),
    "deepseek-v3": (0.27, 0.41),

    # Mistral AI (OpenAI-compatible API)
    "mistral-large-latest": (0.50, 1.50),
    "mistral-large-3": (0.50, 1.50),
    "mistral-medium-latest": (0.40, 2.00),
    "mistral-medium-3": (0.40, 2.00),
    "mistral-small-latest": (0.06, 0.18),

    # Groq (Llama) — hosted on Groq LPU
    "meta-llama/llama-4-maverick-17b-128e-instruct": (0.20, 0.60),
    "llama-4-maverick": (0.20, 0.60),
    "meta-llama/llama-4-scout-17b-16e-instruct": (0.11, 0.34),
    "llama-4-scout": (0.11, 0.34),

    # Meta / Llama (self-hosted)
    "llama-4-scout-17b-16e-instruct": (0.0, 0.0),
    "llama-4-maverick-17b-128e-instruct": (0.0, 0.0),
    "llama-4-scout": (0.0, 0.0),
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost for token usage.

    Args:
        model: Model name (e.g., "gpt-4o", "claude-opus-4")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD

    Example:
        >>> calculate_cost("gpt-4o", 1000, 500)
        0.0075  # $2.50/1M input + $10.00/1M output
    """
    if model not in MODEL_PRICING:
        # Default to mid-tier pricing for unknown models
        return (input_tokens * 3.0 + output_tokens * 15.0) / 1_000_000

    input_price, output_price = MODEL_PRICING[model]
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses simple approximation: 1 token ≈ 4 characters.
    For more accurate counting, use provider-specific tokenizers (e.g., tiktoken).

    Args:
        text: Input text

    Returns:
        Estimated token count

    Example:
        >>> estimate_tokens("Hello, world!")
        3  # 13 chars / 4 ≈ 3 tokens
    """
    return len(text) // 4


def get_model_pricing(model: str) -> Optional[tuple[float, float]]:
    """
    Get pricing for a specific model.

    Args:
        model: Model name

    Returns:
        Tuple of (input_price_per_1m, output_price_per_1m) or None if not found

    Example:
        >>> get_model_pricing("gpt-4o")
        (2.50, 10.00)
    """
    return MODEL_PRICING.get(model)


def get_all_models() -> list[str]:
    """
    Get list of all models with known pricing.

    Returns:
        List of model names
    """
    return list(MODEL_PRICING.keys())


def add_custom_pricing(model: str, input_price: float, output_price: float) -> None:
    """
    Add custom pricing for a model at runtime.

    Useful for new models or custom deployments.

    Args:
        model: Model name
        input_price: Price per 1M input tokens in USD
        output_price: Price per 1M output tokens in USD

    Example:
        >>> add_custom_pricing("custom-model", 5.00, 20.00)
    """
    MODEL_PRICING[model] = (input_price, output_price)


# Alias for backward compatibility with Streamlit frontend
estimate_cost = calculate_cost
