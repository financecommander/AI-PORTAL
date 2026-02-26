"""Token estimation and cost calculation for FastAPI backend.

This module re-exports pricing functions from the shared pricing module.
All pricing data is now centralized in shared/ to eliminate duplication.

For new code, prefer importing directly from shared:
    from shared import calculate_cost, estimate_tokens, MODEL_PRICING
"""

from typing import Optional

# Import from shared module (add parent directory to path if needed)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from shared import (
    MODEL_PRICING,
    calculate_cost,
    estimate_cost,
    estimate_tokens,
    get_model_pricing,
    get_all_models,
    add_custom_pricing,
)

# Re-export for backward compatibility
__all__ = [
    "MODEL_PRICING",
    "calculate_cost",
    "estimate_cost",
    "estimate_tokens",
    "get_model_pricing",
    "get_all_models",
    "add_custom_pricing",
]
