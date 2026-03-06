"""
Benchmark Runner — executes evaluation suites against models.

Supports pluggable benchmark suites that define task sets, scoring functions,
and expected outputs. The runner orchestrates execution and records results
via EvaluationRecorder.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from backend.evaluation.recorder import (
    EvaluationMetrics,
    EvaluationRecord,
    EvaluationRecorder,
)

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTask:
    """A single evaluation task (prompt + expected output)."""

    task_id: str
    prompt: str
    expected_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of executing a single benchmark task."""

    task_id: str
    model_output: str
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    passed: Optional[bool] = None
    score: Optional[float] = None
    error: Optional[str] = None


class BenchmarkSuite(ABC):
    """
    Abstract benchmark suite.

    Subclass this to define a specific evaluation benchmark.
    Each suite provides tasks, a scoring function, and aggregation.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version

    @abstractmethod
    def get_tasks(self) -> List[BenchmarkTask]:
        """Return the list of tasks in this benchmark."""
        ...

    @abstractmethod
    def score_task(self, task: BenchmarkTask, result: TaskResult) -> TaskResult:
        """Score a single task result. Should set result.passed and/or result.score."""
        ...

    def aggregate_metrics(self, results: List[TaskResult]) -> EvaluationMetrics:
        """Aggregate task-level results into summary metrics."""
        scored = [r for r in results if r.score is not None]
        passed = [r for r in results if r.passed is True]
        latencies = [r.latency_ms for r in results if r.error is None]
        tokens = sum(r.output_tokens for r in results)
        total_time = sum(r.latency_ms for r in results) / 1000.0 if results else 0

        accuracy = len(passed) / len(results) if results else 0.0
        mean_score = sum(r.score for r in scored) / len(scored) if scored else None
        mean_latency = sum(latencies) / len(latencies) if latencies else None
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else mean_latency
        tps = tokens / total_time if total_time > 0 else None
        total_cost = sum(r.cost_usd for r in results)

        return EvaluationMetrics(
            accuracy=accuracy,
            pass_at_1=mean_score,
            mean_latency_ms=mean_latency,
            p95_latency_ms=p95_latency,
            tokens_per_second=tps,
            cost_per_task_usd=total_cost / len(results) if results else None,
        )


class CodingAccuracySuite(BenchmarkSuite):
    """Built-in coding accuracy benchmark using simple code completion tasks."""

    TASKS = [
        BenchmarkTask("code_01", "Write a Python function that returns the factorial of n.", "def factorial(n):"),
        BenchmarkTask("code_02", "Write a Python function to check if a string is a palindrome.", "def is_palindrome(s):"),
        BenchmarkTask("code_03", "Write a Python function to find the nth Fibonacci number.", "def fibonacci(n):"),
        BenchmarkTask("code_04", "Write a Python function to reverse a linked list.", "def reverse_linked_list(head):"),
        BenchmarkTask("code_05", "Write a Python function to merge two sorted arrays.", "def merge_sorted(a, b):"),
    ]

    def __init__(self):
        super().__init__("coding_accuracy", "1.0.0")

    def get_tasks(self) -> List[BenchmarkTask]:
        return self.TASKS

    def score_task(self, task: BenchmarkTask, result: TaskResult) -> TaskResult:
        if result.error:
            result.passed = False
            result.score = 0.0
            return result
        # Check if output contains the expected signature
        if task.expected_output and task.expected_output in result.model_output:
            result.passed = True
            result.score = 1.0
        else:
            result.passed = False
            result.score = 0.0
        return result


class ReasoningLogicSuite(BenchmarkSuite):
    """Built-in logical reasoning benchmark."""

    TASKS = [
        BenchmarkTask("logic_01", "If all roses are flowers and all flowers need water, do roses need water? Answer yes or no.", "yes"),
        BenchmarkTask("logic_02", "A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost? Answer with just the number.", "0.05"),
        BenchmarkTask("logic_03", "If it takes 5 machines 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets? Answer in minutes.", "5"),
    ]

    def __init__(self):
        super().__init__("reasoning_logic", "1.0.0")

    def get_tasks(self) -> List[BenchmarkTask]:
        return self.TASKS

    def score_task(self, task: BenchmarkTask, result: TaskResult) -> TaskResult:
        if result.error:
            result.passed = False
            result.score = 0.0
            return result
        output_lower = result.model_output.strip().lower()
        expected_lower = task.expected_output.lower() if task.expected_output else ""
        result.passed = expected_lower in output_lower
        result.score = 1.0 if result.passed else 0.0
        return result


# Registry of built-in suites
BUILTIN_SUITES: Dict[str, type] = {
    "coding_accuracy": CodingAccuracySuite,
    "reasoning_logic": ReasoningLogicSuite,
}


class BenchmarkRunner:
    """
    Orchestrates benchmark execution.

    Runs a benchmark suite against a model (via a provider callable),
    scores results, aggregates metrics, and records via EvaluationRecorder.
    """

    def __init__(self, recorder: EvaluationRecorder):
        self.recorder = recorder
        self._suites: Dict[str, BenchmarkSuite] = {}
        # Register built-ins
        for name, suite_cls in BUILTIN_SUITES.items():
            self._suites[name] = suite_cls()

    def register_suite(self, suite: BenchmarkSuite) -> None:
        """Register a custom benchmark suite."""
        self._suites[suite.name] = suite
        logger.info("Registered benchmark suite: %s v%s", suite.name, suite.version)

    def list_suites(self) -> List[Dict[str, str]]:
        """List available benchmark suites."""
        return [
            {"name": s.name, "version": s.version, "tasks": len(s.get_tasks())}
            for s in self._suites.values()
        ]

    async def run(
        self,
        benchmark_name: str,
        model_name: str,
        model_version: str,
        send_fn: Callable,
        *,
        run_by: Optional[str] = None,
        seed: Optional[int] = None,
        comparison_baseline: Optional[str] = None,
    ) -> EvaluationRecord:
        """
        Execute a benchmark suite against a model.

        Args:
            benchmark_name: Name of the benchmark suite to run.
            model_name: Model being evaluated.
            model_version: Exact version of the model.
            send_fn: Async callable(prompt: str) -> ProviderResponse.
                     Must return an object with .content, .input_tokens,
                     .output_tokens, .latency_ms, .cost_usd attributes.
            run_by: Who triggered this evaluation.
            seed: Random seed for reproducibility.
            comparison_baseline: Model to compare against.

        Returns:
            Completed EvaluationRecord with metrics and verdict.
        """
        if benchmark_name not in self._suites:
            available = list(self._suites.keys())
            raise KeyError(
                f"Benchmark '{benchmark_name}' not found. Available: {available}"
            )

        suite = self._suites[benchmark_name]
        tasks = suite.get_tasks()

        # Create the evaluation record
        from backend.evaluation.recorder import Reproducibility

        record = self.recorder.create(
            model_name=model_name,
            model_version=model_version,
            benchmark=benchmark_name,
            run_by=run_by,
            benchmark_version=suite.version,
            comparison_baseline=comparison_baseline,
            reproducibility=Reproducibility(seed=seed),
        )

        logger.info(
            "Running benchmark %s (%d tasks) for %s/%s",
            benchmark_name, len(tasks), model_name, model_version,
        )

        # Execute tasks
        results: List[TaskResult] = []
        for task in tasks:
            try:
                start = time.monotonic()
                response = await send_fn(task.prompt)
                elapsed_ms = (time.monotonic() - start) * 1000

                result = TaskResult(
                    task_id=task.task_id,
                    model_output=response.content,
                    latency_ms=elapsed_ms,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost_usd=getattr(response, "cost_usd", 0.0),
                )
            except Exception as e:
                result = TaskResult(
                    task_id=task.task_id,
                    model_output="",
                    latency_ms=0.0,
                    error=str(e),
                )

            # Score the task
            result = suite.score_task(task, result)
            results.append(result)

        # Aggregate metrics
        metrics = suite.aggregate_metrics(results)

        # Determine verdict
        verdict = self._determine_verdict(metrics, comparison_baseline)

        # Record completion
        completed = self.recorder.complete(
            record.evaluation_id,
            metrics=metrics,
            verdict=verdict,
        )

        logger.info(
            "Benchmark %s complete: accuracy=%.2f, verdict=%s",
            benchmark_name,
            metrics.accuracy or 0,
            verdict,
        )

        return completed

    def _determine_verdict(
        self,
        metrics: EvaluationMetrics,
        comparison_baseline: Optional[str],
    ) -> Optional[str]:
        """Determine pass/fail verdict based on metrics."""
        if metrics.accuracy is None:
            return None
        if metrics.accuracy >= 0.8:
            return "pass"
        elif metrics.accuracy >= 0.5:
            return "neutral"
        else:
            return "fail"
