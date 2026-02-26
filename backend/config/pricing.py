"""Pricing table. Single source of truth for all cost calculations.

NOTE: backend/utils/token_estimator.py has its own MODEL_PRICING dict.
This file is the authoritative source. When they diverge, update token_estimator.py.
"""

PRICING: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4o": {"input_per_1m": 2.50, "output_per_1m": 10.00},
    "gpt-4o-mini": {"input_per_1m": 0.15, "output_per_1m": 0.60},
    "o1": {"input_per_1m": 15.00, "output_per_1m": 60.00},
    "o3-mini": {"input_per_1m": 1.10, "output_per_1m": 4.40},
    # Anthropic
    "claude-opus-4-20250514": {"input_per_1m": 15.00, "output_per_1m": 75.00},
    "claude-sonnet-4-5-20250929": {"input_per_1m": 3.00, "output_per_1m": 15.00},
    "claude-haiku-4-5-20251001": {"input_per_1m": 0.80, "output_per_1m": 4.00},
    # Google
    "gemini-2.0-flash": {"input_per_1m": 0.10, "output_per_1m": 0.40},
    "gemini-2.0-flash-exp": {"input_per_1m": 0.10, "output_per_1m": 0.40},
    # xAI (Grok)
    "grok-beta": {"input_per_1m": 5.00, "output_per_1m": 15.00},
    "grok-3": {"input_per_1m": 3.00, "output_per_1m": 15.00},
    # Groq (Llama)
    "llama-3.1-405b-reasoning": {"input_per_1m": 0.59, "output_per_1m": 0.79},
    "llama-3.1-70b-versatile": {"input_per_1m": 0.29, "output_per_1m": 0.39},
}

DEFAULT_PRICING = {"input_per_1m": 10.00, "output_per_1m": 30.00}
