"""
Model Registry — Gap #4.

Versioned model lifecycle management implementing model.schema.json.
AI-PORTAL owns the model lifecycle: train → evaluate → register → deploy → monitor.

Per GOVERNANCE.md: This module materializes the model registry ownership.
"""

from backend.model_registry.registry import ModelRegistry, ModelRecord

__all__ = [
    "ModelRegistry",
    "ModelRecord",
]
