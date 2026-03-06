"""
Model Comparator — compares evaluation results across models.

Enables side-by-side comparison of evaluation metrics for model selection
and regression detection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.evaluation.recorder import EvaluationRecord, EvaluationRecorder

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Result of comparing two or more model evaluations."""

    benchmark: str
    models: List[str]
    metrics_comparison: Dict[str, Dict[str, Any]]  # metric_name -> {model: value}
    winner: Optional[str] = None
    verdict: Optional[str] = None  # "improvement", "regression", "neutral"
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark": self.benchmark,
            "models": self.models,
            "metrics_comparison": self.metrics_comparison,
            "winner": self.winner,
            "verdict": self.verdict,
            "details": self.details,
        }


class ModelComparator:
    """
    Compares evaluation results across models on the same benchmark.

    Usage:
        comparator = ModelComparator(recorder)
        result = comparator.compare("coding_accuracy", ["gpt-4o/1.0", "llama-3/1.0"])
    """

    def __init__(self, recorder: EvaluationRecorder):
        self.recorder = recorder

    def compare(
        self,
        benchmark: str,
        model_specs: List[str],
    ) -> ComparisonResult:
        """
        Compare models on a specific benchmark.

        Args:
            benchmark: Benchmark name to compare on.
            model_specs: List of "model_name/model_version" strings.

        Returns:
            ComparisonResult with side-by-side metrics.
        """
        metrics_comparison: Dict[str, Dict[str, Any]] = {}
        model_records: Dict[str, EvaluationRecord] = {}

        for spec in model_specs:
            parts = spec.split("/", 1)
            model_name = parts[0]
            model_version = parts[1] if len(parts) > 1 else None

            # Find the latest evaluation for this model on this benchmark
            records = self.recorder.list_records(
                model_name=model_name, benchmark=benchmark
            )
            if model_version:
                records = [r for r in records if r.model_version == model_version]

            if not records:
                logger.warning("No evaluation found for %s on %s", spec, benchmark)
                continue

            record = records[0]  # latest
            model_records[spec] = record

            # Extract metrics
            metrics_dict = record.metrics.to_dict()
            for metric_name, value in metrics_dict.items():
                if metric_name not in metrics_comparison:
                    metrics_comparison[metric_name] = {}
                metrics_comparison[metric_name][spec] = value

        # Determine winner based on accuracy (primary metric)
        winner = None
        if "accuracy" in metrics_comparison:
            accuracy_scores = metrics_comparison["accuracy"]
            if accuracy_scores:
                winner = max(accuracy_scores, key=lambda k: accuracy_scores.get(k, 0) or 0)

        # Determine verdict
        verdict = None
        if len(model_specs) == 2 and len(model_records) == 2:
            specs = list(model_records.keys())
            acc_0 = (metrics_comparison.get("accuracy", {}).get(specs[0]) or 0)
            acc_1 = (metrics_comparison.get("accuracy", {}).get(specs[1]) or 0)
            diff = acc_1 - acc_0
            if diff > 0.05:
                verdict = "improvement"
            elif diff < -0.05:
                verdict = "regression"
            else:
                verdict = "neutral"

        details_parts = []
        for metric_name, values in sorted(metrics_comparison.items()):
            formatted = ", ".join(f"{k}: {v}" for k, v in values.items())
            details_parts.append(f"  {metric_name}: {formatted}")
        details = "\n".join(details_parts)

        return ComparisonResult(
            benchmark=benchmark,
            models=model_specs,
            metrics_comparison=metrics_comparison,
            winner=winner,
            verdict=verdict,
            details=details,
        )

    def regression_check(
        self,
        model_name: str,
        current_version: str,
        previous_version: str,
        benchmark: str,
        threshold: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Check for regressions between two versions of the same model.

        Returns dict with 'regressed' bool, 'metrics_delta', and 'details'.
        """
        result = self.compare(
            benchmark,
            [f"{model_name}/{previous_version}", f"{model_name}/{current_version}"],
        )

        deltas = {}
        regressed_metrics = []
        for metric, values in result.metrics_comparison.items():
            prev_key = f"{model_name}/{previous_version}"
            curr_key = f"{model_name}/{current_version}"
            prev_val = values.get(prev_key)
            curr_val = values.get(curr_key)
            if prev_val is not None and curr_val is not None:
                delta = curr_val - prev_val
                deltas[metric] = delta
                # Higher is better for accuracy-like metrics
                if metric in ("accuracy", "pass_at_1", "pass_at_5",
                              "merge_success_rate", "tokens_per_second",
                              "token_efficiency"):
                    if delta < -threshold:
                        regressed_metrics.append(metric)
                # Lower is better for latency/cost metrics
                elif metric in ("mean_latency_ms", "p95_latency_ms",
                                "p99_latency_ms", "cost_per_task_usd",
                                "memory_peak_mb"):
                    if delta > threshold:
                        regressed_metrics.append(metric)

        return {
            "regressed": len(regressed_metrics) > 0,
            "regressed_metrics": regressed_metrics,
            "metrics_delta": deltas,
            "comparison": result.to_dict(),
        }
