"""
Evaluation Recorder — persists evaluation results per evaluation.schema.json.

Stores EvaluationRecord objects in-memory (with JSON file persistence) so
they can be queried for comparisons and dashboards.
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

# Canonical benchmark names (from evaluation.schema.json)
VALID_BENCHMARKS = frozenset([
    "coding_accuracy",
    "coding_completion",
    "reasoning_logic",
    "reasoning_math",
    "merge_validation",
    "latency_throughput",
    "token_efficiency",
    "resource_consumption",
    "domain_finance",
    "domain_underwriting",
    "domain_compliance",
    "custom",
])

VALID_VERDICTS = frozenset([None, "pass", "fail", "regression", "improvement", "neutral"])


@dataclass
class EvaluationMetrics:
    """Standard evaluation metrics (all optional)."""

    accuracy: Optional[float] = None
    pass_at_1: Optional[float] = None
    pass_at_5: Optional[float] = None
    merge_success_rate: Optional[float] = None
    mean_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    tokens_per_second: Optional[float] = None
    token_efficiency: Optional[float] = None
    cost_per_task_usd: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    # Custom metrics stored here
    extra: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for k, v in asdict(self).items():
            if k == "extra":
                d.update(v)
            elif v is not None:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationMetrics":
        known = {f.name for f in cls.__dataclass_fields__.values() if f.name != "extra"}
        kwargs = {}
        extra = {}
        for k, v in data.items():
            if k in known:
                kwargs[k] = v
            else:
                extra[k] = v
        kwargs["extra"] = extra
        return cls(**kwargs)


@dataclass
class Reproducibility:
    """Deterministic execution metadata."""

    seed: Optional[int] = None
    runtime_environment: Optional[str] = None
    task_version: Optional[str] = None
    config_snapshot: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationRecord:
    """
    Canonical evaluation record — maps 1:1 to evaluation.schema.json.

    Create via ``EvaluationRecorder.create()`` for auto-generated IDs and
    timestamps, or construct directly for imported records.
    """

    evaluation_id: str
    model_name: str
    model_version: str
    benchmark: str
    started_at: str  # ISO-8601
    benchmark_version: Optional[str] = None
    metrics: EvaluationMetrics = field(default_factory=EvaluationMetrics)
    dataset_ref: Optional[str] = None
    dataset_version: Optional[str] = None
    reproducibility: Reproducibility = field(default_factory=Reproducibility)
    comparison_baseline: Optional[str] = None
    verdict: Optional[str] = None
    artifact_refs: List[str] = field(default_factory=list)
    completed_at: Optional[str] = None
    run_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.benchmark not in VALID_BENCHMARKS:
            raise ValueError(
                f"Invalid benchmark '{self.benchmark}'. "
                f"Must be one of: {sorted(VALID_BENCHMARKS)}"
            )
        if self.verdict not in VALID_VERDICTS:
            raise ValueError(
                f"Invalid verdict '{self.verdict}'. "
                f"Must be one of: {sorted(VALID_VERDICTS - {None})}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict matching evaluation.schema.json."""
        return {
            "evaluation_id": self.evaluation_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "benchmark": self.benchmark,
            "benchmark_version": self.benchmark_version,
            "metrics": self.metrics.to_dict(),
            "dataset_ref": self.dataset_ref,
            "dataset_version": self.dataset_version,
            "reproducibility": asdict(self.reproducibility),
            "comparison_baseline": self.comparison_baseline,
            "verdict": self.verdict,
            "artifact_refs": self.artifact_refs,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "run_by": self.run_by,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationRecord":
        """Deserialize from dict."""
        metrics = EvaluationMetrics.from_dict(data.get("metrics", {}))
        repro_data = data.get("reproducibility", {})
        repro = Reproducibility(**repro_data) if repro_data else Reproducibility()
        return cls(
            evaluation_id=data["evaluation_id"],
            model_name=data["model_name"],
            model_version=data["model_version"],
            benchmark=data["benchmark"],
            started_at=data["started_at"],
            benchmark_version=data.get("benchmark_version"),
            metrics=metrics,
            dataset_ref=data.get("dataset_ref"),
            dataset_version=data.get("dataset_version"),
            reproducibility=repro,
            comparison_baseline=data.get("comparison_baseline"),
            verdict=data.get("verdict"),
            artifact_refs=data.get("artifact_refs", []),
            completed_at=data.get("completed_at"),
            run_by=data.get("run_by"),
            tags=data.get("tags", {}),
        )


class EvaluationRecorder:
    """
    Persistent store for evaluation records.

    Records are kept in memory and optionally persisted to a JSON file.
    In production this would back onto PostgreSQL via SQLModel.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self._records: Dict[str, EvaluationRecord] = {}
        self._storage_path = storage_path
        if storage_path and storage_path.exists():
            self._load()

    # ── CRUD ────────────────────────────────────────────────────────

    def create(
        self,
        model_name: str,
        model_version: str,
        benchmark: str,
        *,
        run_by: Optional[str] = None,
        **kwargs,
    ) -> EvaluationRecord:
        """Create a new evaluation record with auto-generated ID and timestamp."""
        record = EvaluationRecord(
            evaluation_id=f"eval-{uuid.uuid4().hex[:12]}",
            model_name=model_name,
            model_version=model_version,
            benchmark=benchmark,
            started_at=datetime.now(timezone.utc).isoformat(),
            run_by=run_by,
            **kwargs,
        )
        self._records[record.evaluation_id] = record
        self._save()
        logger.info(
            "Created evaluation %s: %s/%s on %s",
            record.evaluation_id, model_name, model_version, benchmark,
        )
        return record

    def get(self, evaluation_id: str) -> Optional[EvaluationRecord]:
        return self._records.get(evaluation_id)

    def complete(
        self,
        evaluation_id: str,
        metrics: EvaluationMetrics,
        verdict: Optional[str] = None,
        artifact_refs: Optional[List[str]] = None,
    ) -> EvaluationRecord:
        """Mark an evaluation as completed with results."""
        record = self._records.get(evaluation_id)
        if record is None:
            raise KeyError(f"Evaluation '{evaluation_id}' not found")
        record.metrics = metrics
        record.verdict = verdict
        record.completed_at = datetime.now(timezone.utc).isoformat()
        if artifact_refs:
            record.artifact_refs.extend(artifact_refs)
        self._save()
        logger.info("Completed evaluation %s — verdict=%s", evaluation_id, verdict)
        return record

    def list_records(
        self,
        model_name: Optional[str] = None,
        benchmark: Optional[str] = None,
        limit: int = 100,
    ) -> List[EvaluationRecord]:
        """List evaluation records with optional filters."""
        results = list(self._records.values())
        if model_name:
            results = [r for r in results if r.model_name == model_name]
        if benchmark:
            results = [r for r in results if r.benchmark == benchmark]
        # Sort by started_at descending
        results.sort(key=lambda r: r.started_at, reverse=True)
        return results[:limit]

    def delete(self, evaluation_id: str) -> bool:
        if evaluation_id in self._records:
            del self._records[evaluation_id]
            self._save()
            return True
        return False

    # ── Persistence ─────────────────────────────────────────────────

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = [r.to_dict() for r in self._records.values()]
        self._storage_path.write_text(json.dumps(data, indent=2))

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        try:
            data = json.loads(self._storage_path.read_text())
            for item in data:
                record = EvaluationRecord.from_dict(item)
                self._records[record.evaluation_id] = record
            logger.info("Loaded %d evaluation records", len(self._records))
        except Exception as e:
            logger.error("Failed to load evaluation records: %s", e)
