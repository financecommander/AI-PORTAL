"""Per-model token pricing for Streamlit frontend.

This module re-exports pricing functions from the shared pricing module.
All pricing data is now centralized in shared/ to eliminate duplication.

For new code, prefer importing directly from shared:
    from shared import calculate_cost, estimate_tokens, MODEL_PRICING
"""

# Import from shared module
from shared import (
    MODEL_PRICING,
    calculate_cost,
    estimate_cost,  # Alias for calculate_cost
    estimate_tokens,
    get_model_pricing,
    get_all_models,
    add_custom_pricing,
)

# Re-export for backward compatibility
__all__ = [
    "MODEL_PRICING",
    "estimate_cost",
    "calculate_cost",
    "estimate_tokens",
    "get_model_pricing",
    "get_all_models",
    "add_custom_pricing",
]
