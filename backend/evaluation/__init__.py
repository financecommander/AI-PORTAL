"""
Evaluation Framework — Gap #3.

Benchmark runner, metrics recorder, and comparison engine for model evaluation.
Implements the EvaluationRecord schema from protocol/evaluation.schema.json.

Per GOVERNANCE.md: AI-PORTAL owns the evaluation framework (benchmark datasets,
runner, dashboards). This module materializes that ownership.
"""

from backend.evaluation.runner import BenchmarkRunner, BenchmarkSuite
from backend.evaluation.recorder import EvaluationRecorder, EvaluationRecord
from backend.evaluation.comparator import ModelComparator

__all__ = [
    "BenchmarkRunner",
    "BenchmarkSuite",
    "EvaluationRecorder",
    "EvaluationRecord",
    "ModelComparator",
]
