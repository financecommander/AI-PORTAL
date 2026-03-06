"""
Model Registry — versioned model metadata store per model.schema.json.

Manages the full model lifecycle:
  registered → evaluating → staging → deployed → deprecated → archived

Stores ModelRecord objects in-memory with JSON file persistence.
In production, this would back onto PostgreSQL via SQLModel.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Canonical values from model.schema.json
VALID_MODEL_TYPES = frozenset([
    "teacher",
    "student",
    "ternary_student",
    "fine_tuned",
    "base",
    "adapter",
    "quantized",
    "ensemble",
])

VALID_PROVIDERS = frozenset([
    None, "ollama", "triton", "openai", "anthropic", "xai",
    "deepseek", "groq", "mistral", "google", "local",
])

VALID_QUANTIZATIONS = frozenset([
    None, "ternary", "binary", "int4", "int8",
    "fp16", "bf16", "fp32", "Q4_K_M", "Q5_K_M", "Q8_0",
])

VALID_STATUSES = frozenset([
    "registered", "evaluating", "staging",
    "deployed", "deprecated", "archived",
])

VALID_RUNTIME_TARGETS = frozenset([
    "cpu", "cuda", "triton_ternary", "edge", "wasm", "metal", "vulkan",
])

# Valid lifecycle transitions
_TRANSITIONS = {
    "registered":  ["evaluating", "staging", "archived"],
    "evaluating":  ["staging", "registered", "archived"],
    "staging":     ["deployed", "evaluating", "archived"],
    "deployed":    ["deprecated", "staging"],
    "deprecated":  ["archived", "deployed"],
    "archived":    [],  # terminal state
}


@dataclass
class ModelRecord:
    """
    Model metadata record — maps 1:1 to model.schema.json.

    Each record represents a specific version of a model in the registry.
    """

    model_name: str
    model_version: str
    model_type: str
    registered_at: str  # ISO-8601

    # Optional fields
    provider: Optional[str] = None
    architecture: Optional[str] = None
    parameter_count: Optional[int] = None
    quantization: Optional[str] = None
    compression_ratio: Optional[float] = None
    training_dataset: Optional[str] = None
    training_config: Dict[str, Any] = field(default_factory=dict)
    evaluation_scores: Dict[str, float] = field(default_factory=dict)
    runtime_targets: List[str] = field(default_factory=lambda: ["cpu"])
    cost_per_1m_input: Optional[float] = None
    cost_per_1m_output: Optional[float] = None
    max_context_tokens: Optional[int] = None
    artifact_ref: Optional[str] = None
    parent_model: Optional[str] = None
    registered_by: Optional[str] = None
    deployment_status: str = "registered"
    tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.model_type not in VALID_MODEL_TYPES:
            raise ValueError(f"Invalid model_type '{self.model_type}'. Must be one of: {sorted(VALID_MODEL_TYPES)}")
        if self.provider not in VALID_PROVIDERS:
            raise ValueError(f"Invalid provider '{self.provider}'. Must be one of: {sorted(VALID_PROVIDERS - {None})}")
        if self.quantization not in VALID_QUANTIZATIONS:
            raise ValueError(f"Invalid quantization '{self.quantization}'.")
        if self.deployment_status not in VALID_STATUSES:
            raise ValueError(f"Invalid deployment_status '{self.deployment_status}'.")
        for rt in self.runtime_targets:
            if rt not in VALID_RUNTIME_TARGETS:
                raise ValueError(f"Invalid runtime target '{rt}'.")

    @property
    def key(self) -> str:
        """Unique key: model_name/model_version."""
        return f"{self.model_name}/{self.model_version}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict matching model.schema.json."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelRecord":
        """Deserialize from dict."""
        return cls(**data)


class ModelRegistry:
    """
    Versioned model registry with lifecycle management.

    Supports:
    - Register new model versions
    - Lifecycle transitions (registered → evaluating → staging → deployed → ...)
    - Query by name, type, provider, status
    - Attach evaluation scores
    - JSON file persistence
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self._models: Dict[str, ModelRecord] = {}  # key: "name/version"
        self._storage_path = storage_path
        if storage_path and storage_path.exists():
            self._load()

    # ── Registration ─────────────────────────────────────────────

    def register(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        *,
        registered_by: Optional[str] = None,
        **kwargs,
    ) -> ModelRecord:
        """
        Register a new model version.

        Raises ValueError if this exact name/version already exists.
        """
        key = f"{model_name}/{model_version}"
        if key in self._models:
            raise ValueError(f"Model '{key}' already registered. Use a new version.")

        record = ModelRecord(
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            registered_at=datetime.now(timezone.utc).isoformat(),
            registered_by=registered_by,
            **kwargs,
        )
        self._models[key] = record
        self._save()
        logger.info("Registered model %s (type=%s, provider=%s)", key, model_type, record.provider)
        return record

    # ── Lifecycle ────────────────────────────────────────────────

    def transition(self, model_name: str, model_version: str, new_status: str) -> ModelRecord:
        """
        Transition a model to a new lifecycle status.

        Validates the transition is legal per the state machine.
        """
        key = f"{model_name}/{model_version}"
        record = self._models.get(key)
        if record is None:
            raise KeyError(f"Model '{key}' not found in registry")

        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'")

        allowed = _TRANSITIONS.get(record.deployment_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition '{key}' from '{record.deployment_status}' "
                f"to '{new_status}'. Allowed: {allowed}"
            )

        old_status = record.deployment_status
        record.deployment_status = new_status
        self._save()
        logger.info("Model %s: %s → %s", key, old_status, new_status)
        return record

    def promote(self, model_name: str, model_version: str) -> ModelRecord:
        """Promote model one step forward in the lifecycle."""
        key = f"{model_name}/{model_version}"
        record = self._models.get(key)
        if record is None:
            raise KeyError(f"Model '{key}' not found")

        promotion_path = {
            "registered": "evaluating",
            "evaluating": "staging",
            "staging": "deployed",
        }
        next_status = promotion_path.get(record.deployment_status)
        if next_status is None:
            raise ValueError(
                f"Cannot promote model in '{record.deployment_status}' state"
            )
        return self.transition(model_name, model_version, next_status)

    def deprecate(self, model_name: str, model_version: str) -> ModelRecord:
        """Deprecate a deployed model."""
        return self.transition(model_name, model_version, "deprecated")

    # ── Query ────────────────────────────────────────────────────

    def get(self, model_name: str, model_version: str) -> Optional[ModelRecord]:
        """Get a specific model version."""
        return self._models.get(f"{model_name}/{model_version}")

    def get_latest(self, model_name: str) -> Optional[ModelRecord]:
        """Get the latest version of a model (by registration date)."""
        candidates = [
            r for r in self._models.values() if r.model_name == model_name
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda r: r.registered_at, reverse=True)
        return candidates[0]

    def list_models(
        self,
        model_type: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[ModelRecord]:
        """List models with optional filters."""
        results = list(self._models.values())
        if model_type:
            results = [r for r in results if r.model_type == model_type]
        if provider:
            results = [r for r in results if r.provider == provider]
        if status:
            results = [r for r in results if r.deployment_status == status]
        results.sort(key=lambda r: r.registered_at, reverse=True)
        return results[:limit]

    def list_versions(self, model_name: str) -> List[ModelRecord]:
        """List all versions of a specific model."""
        results = [r for r in self._models.values() if r.model_name == model_name]
        results.sort(key=lambda r: r.registered_at, reverse=True)
        return results

    def delete(self, model_name: str, model_version: str) -> bool:
        """Delete a model from the registry (only if archived)."""
        key = f"{model_name}/{model_version}"
        record = self._models.get(key)
        if record is None:
            return False
        if record.deployment_status != "archived":
            raise ValueError(
                f"Cannot delete model in '{record.deployment_status}' state. "
                f"Archive it first."
            )
        del self._models[key]
        self._save()
        return True

    # ── Evaluation scores ─────────────────────────────────────────

    def update_scores(
        self,
        model_name: str,
        model_version: str,
        scores: Dict[str, float],
    ) -> ModelRecord:
        """Attach evaluation benchmark scores to a model."""
        key = f"{model_name}/{model_version}"
        record = self._models.get(key)
        if record is None:
            raise KeyError(f"Model '{key}' not found")
        record.evaluation_scores.update(scores)
        self._save()
        return record

    # ── Persistence ──────────────────────────────────────────────

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = [r.to_dict() for r in self._models.values()]
        self._storage_path.write_text(json.dumps(data, indent=2))

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        try:
            data = json.loads(self._storage_path.read_text())
            for item in data:
                record = ModelRecord.from_dict(item)
                self._models[record.key] = record
            logger.info("Loaded %d model records", len(self._models))
        except Exception as e:
            logger.error("Failed to load model registry: %s", e)

    @property
    def count(self) -> int:
        return len(self._models)
