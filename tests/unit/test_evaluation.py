"""
Tests for the evaluation framework (Gap #3) and model registry (Gap #4).
"""

import asyncio
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

# =====================================================================
# Evaluation Framework Tests
# =====================================================================


class TestEvaluationRecorder:
    """Tests for EvaluationRecorder CRUD and persistence."""

    def test_create_record(self):
        from backend.evaluation.recorder import EvaluationRecorder
        rec = EvaluationRecorder()
        record = rec.create("gpt-4o", "1.0.0", "coding_accuracy")
        assert record.evaluation_id.startswith("eval-")
        assert record.model_name == "gpt-4o"
        assert record.benchmark == "coding_accuracy"
        assert record.started_at is not None

    def test_get_record(self):
        from backend.evaluation.recorder import EvaluationRecorder
        rec = EvaluationRecorder()
        record = rec.create("gpt-4o", "1.0.0", "reasoning_logic")
        fetched = rec.get(record.evaluation_id)
        assert fetched is not None
        assert fetched.evaluation_id == record.evaluation_id

    def test_complete_record(self):
        from backend.evaluation.recorder import EvaluationRecorder, EvaluationMetrics
        rec = EvaluationRecorder()
        record = rec.create("gpt-4o", "1.0.0", "coding_accuracy")
        metrics = EvaluationMetrics(accuracy=0.85, pass_at_1=0.80)
        completed = rec.complete(record.evaluation_id, metrics, verdict="pass")
        assert completed.verdict == "pass"
        assert completed.metrics.accuracy == 0.85
        assert completed.completed_at is not None

    def test_list_records_filter(self):
        from backend.evaluation.recorder import EvaluationRecorder
        rec = EvaluationRecorder()
        rec.create("gpt-4o", "1.0.0", "coding_accuracy")
        rec.create("gpt-4o", "1.0.0", "reasoning_logic")
        rec.create("claude", "3.5.0", "coding_accuracy")

        coding = rec.list_records(benchmark="coding_accuracy")
        assert len(coding) == 2

        gpt_only = rec.list_records(model_name="gpt-4o")
        assert len(gpt_only) == 2

    def test_delete_record(self):
        from backend.evaluation.recorder import EvaluationRecorder
        rec = EvaluationRecorder()
        record = rec.create("gpt-4o", "1.0.0", "coding_accuracy")
        assert rec.delete(record.evaluation_id) is True
        assert rec.get(record.evaluation_id) is None

    def test_invalid_benchmark_raises(self):
        from backend.evaluation.recorder import EvaluationRecord
        with pytest.raises(ValueError, match="Invalid benchmark"):
            EvaluationRecord(
                evaluation_id="test",
                model_name="test",
                model_version="1.0",
                benchmark="invalid_benchmark",
                started_at="2025-01-01T00:00:00Z",
            )

    def test_persistence_roundtrip(self):
        from backend.evaluation.recorder import EvaluationRecorder, EvaluationMetrics
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "evals.json"

            rec1 = EvaluationRecorder(path)
            r = rec1.create("gpt-4o", "1.0.0", "coding_accuracy")
            rec1.complete(r.evaluation_id, EvaluationMetrics(accuracy=0.9), verdict="pass")

            # Load in new instance
            rec2 = EvaluationRecorder(path)
            loaded = rec2.get(r.evaluation_id)
            assert loaded is not None
            assert loaded.metrics.accuracy == 0.9
            assert loaded.verdict == "pass"

    def test_serialization_roundtrip(self):
        from backend.evaluation.recorder import EvaluationRecord, EvaluationMetrics, Reproducibility
        record = EvaluationRecord(
            evaluation_id="eval-test123",
            model_name="llama-3",
            model_version="1.0.0",
            benchmark="coding_accuracy",
            started_at="2025-01-01T00:00:00Z",
            metrics=EvaluationMetrics(accuracy=0.95, pass_at_1=0.90, extra={"custom": 0.5}),
            reproducibility=Reproducibility(seed=42, runtime_environment="python:3.12"),
            verdict="pass",
            tags={"env": "staging"},
        )
        d = record.to_dict()
        restored = EvaluationRecord.from_dict(d)
        assert restored.evaluation_id == "eval-test123"
        assert restored.metrics.accuracy == 0.95
        assert restored.reproducibility.seed == 42


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner execution."""

    def test_list_suites(self):
        from backend.evaluation.recorder import EvaluationRecorder
        from backend.evaluation.runner import BenchmarkRunner
        rec = EvaluationRecorder()
        runner = BenchmarkRunner(rec)
        suites = runner.list_suites()
        names = [s["name"] for s in suites]
        assert "coding_accuracy" in names
        assert "reasoning_logic" in names

    def test_register_custom_suite(self):
        from backend.evaluation.recorder import EvaluationRecorder
        from backend.evaluation.runner import BenchmarkRunner, BenchmarkSuite, BenchmarkTask, TaskResult

        class DummySuite(BenchmarkSuite):
            def get_tasks(self):
                return [BenchmarkTask("t1", "test prompt")]
            def score_task(self, task, result):
                result.passed = True
                result.score = 1.0
                return result

        rec = EvaluationRecorder()
        runner = BenchmarkRunner(rec)
        runner.register_suite(DummySuite("custom", "1.0.0"))
        suites = runner.list_suites()
        assert any(s["name"] == "custom" for s in suites)

    def test_run_benchmark(self):
        from backend.evaluation.recorder import EvaluationRecorder
        from backend.evaluation.runner import BenchmarkRunner

        @dataclass
        class MockResponse:
            content: str = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
            input_tokens: int = 10
            output_tokens: int = 20
            latency_ms: float = 100.0
            cost_usd: float = 0.001

        async def mock_send(prompt: str):
            return MockResponse()

        rec = EvaluationRecorder()
        runner = BenchmarkRunner(rec)
        result = asyncio.get_event_loop().run_until_complete(
            runner.run("coding_accuracy", "test-model", "1.0.0", mock_send)
        )
        assert result.completed_at is not None
        assert result.metrics.accuracy is not None
        assert result.verdict is not None

    def test_unknown_benchmark_raises(self):
        from backend.evaluation.recorder import EvaluationRecorder
        from backend.evaluation.runner import BenchmarkRunner

        async def mock_send(prompt):
            pass

        rec = EvaluationRecorder()
        runner = BenchmarkRunner(rec)
        with pytest.raises(KeyError, match="not found"):
            asyncio.get_event_loop().run_until_complete(
                runner.run("nonexistent", "m", "1.0", mock_send)
            )


class TestModelComparator:
    """Tests for model comparison and regression detection."""

    def test_compare_models(self):
        from backend.evaluation.recorder import EvaluationRecorder, EvaluationMetrics
        from backend.evaluation.comparator import ModelComparator

        rec = EvaluationRecorder()
        r1 = rec.create("gpt-4o", "1.0.0", "coding_accuracy")
        rec.complete(r1.evaluation_id, EvaluationMetrics(accuracy=0.85))
        r2 = rec.create("claude", "3.5.0", "coding_accuracy")
        rec.complete(r2.evaluation_id, EvaluationMetrics(accuracy=0.90))

        comparator = ModelComparator(rec)
        result = comparator.compare("coding_accuracy", ["gpt-4o/1.0.0", "claude/3.5.0"])
        assert result.winner == "claude/3.5.0"
        assert "accuracy" in result.metrics_comparison

    def test_regression_check(self):
        from backend.evaluation.recorder import EvaluationRecorder, EvaluationMetrics
        from backend.evaluation.comparator import ModelComparator

        rec = EvaluationRecorder()
        r1 = rec.create("mymodel", "1.0.0", "coding_accuracy")
        rec.complete(r1.evaluation_id, EvaluationMetrics(accuracy=0.90))
        r2 = rec.create("mymodel", "1.1.0", "coding_accuracy")
        rec.complete(r2.evaluation_id, EvaluationMetrics(accuracy=0.80))

        comparator = ModelComparator(rec)
        result = comparator.regression_check("mymodel", "1.1.0", "1.0.0", "coding_accuracy")
        assert result["regressed"] is True
        assert "accuracy" in result["regressed_metrics"]


# =====================================================================
# Model Registry Tests
# =====================================================================


class TestModelRegistry:
    """Tests for ModelRegistry CRUD and lifecycle management."""

    def test_register_model(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        record = reg.register("gpt-4o", "1.0.0", "teacher", provider="openai")
        assert record.model_name == "gpt-4o"
        assert record.deployment_status == "registered"
        assert record.provider == "openai"

    def test_duplicate_registration_raises(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        with pytest.raises(ValueError, match="already registered"):
            reg.register("gpt-4o", "1.0.0", "teacher")

    def test_invalid_model_type_raises(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        with pytest.raises(ValueError, match="Invalid model_type"):
            reg.register("test", "1.0.0", "invalid_type")

    def test_get_model(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        record = reg.get("gpt-4o", "1.0.0")
        assert record is not None
        assert record.model_name == "gpt-4o"

    def test_get_latest(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        reg.register("gpt-4o", "1.1.0", "teacher")
        latest = reg.get_latest("gpt-4o")
        assert latest is not None
        assert latest.model_version == "1.1.0"

    def test_lifecycle_promote(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")

        reg.promote("gpt-4o", "1.0.0")  # registered → evaluating
        assert reg.get("gpt-4o", "1.0.0").deployment_status == "evaluating"

        reg.promote("gpt-4o", "1.0.0")  # evaluating → staging
        assert reg.get("gpt-4o", "1.0.0").deployment_status == "staging"

        reg.promote("gpt-4o", "1.0.0")  # staging → deployed
        assert reg.get("gpt-4o", "1.0.0").deployment_status == "deployed"

    def test_lifecycle_deprecate(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        reg.promote("gpt-4o", "1.0.0")  # → evaluating
        reg.promote("gpt-4o", "1.0.0")  # → staging
        reg.promote("gpt-4o", "1.0.0")  # → deployed
        reg.deprecate("gpt-4o", "1.0.0")
        assert reg.get("gpt-4o", "1.0.0").deployment_status == "deprecated"

    def test_invalid_transition_raises(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        with pytest.raises(ValueError, match="Cannot transition"):
            reg.transition("gpt-4o", "1.0.0", "deployed")  # can't skip

    def test_list_models_filter(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher", provider="openai")
        reg.register("llama-3", "8b", "base", provider="ollama")
        reg.register("ternary-llama", "1.0.0", "ternary_student", provider="triton")

        teachers = reg.list_models(model_type="teacher")
        assert len(teachers) == 1
        assert teachers[0].model_name == "gpt-4o"

        ollama = reg.list_models(provider="ollama")
        assert len(ollama) == 1

    def test_list_versions(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        reg.register("gpt-4o", "1.1.0", "teacher")
        reg.register("claude", "3.5.0", "teacher")
        versions = reg.list_versions("gpt-4o")
        assert len(versions) == 2

    def test_update_scores(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        reg.update_scores("gpt-4o", "1.0.0", {"coding_accuracy": 0.92, "reasoning_logic": 0.88})
        record = reg.get("gpt-4o", "1.0.0")
        assert record.evaluation_scores["coding_accuracy"] == 0.92

    def test_delete_requires_archived(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        with pytest.raises(ValueError, match="Archive it first"):
            reg.delete("gpt-4o", "1.0.0")

    def test_delete_archived(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        reg.register("gpt-4o", "1.0.0", "teacher")
        reg.transition("gpt-4o", "1.0.0", "archived")
        assert reg.delete("gpt-4o", "1.0.0") is True
        assert reg.get("gpt-4o", "1.0.0") is None

    def test_persistence_roundtrip(self):
        from backend.model_registry.registry import ModelRegistry
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "models.json"
            reg1 = ModelRegistry(path)
            reg1.register("gpt-4o", "1.0.0", "teacher", provider="openai")
            reg1.update_scores("gpt-4o", "1.0.0", {"acc": 0.9})

            reg2 = ModelRegistry(path)
            loaded = reg2.get("gpt-4o", "1.0.0")
            assert loaded is not None
            assert loaded.provider == "openai"
            assert loaded.evaluation_scores["acc"] == 0.9

    def test_count(self):
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        assert reg.count == 0
        reg.register("gpt-4o", "1.0.0", "teacher")
        assert reg.count == 1

    def test_ternary_model_registration(self):
        """Test registering a ternary model (Triton Gap #16 integration)."""
        from backend.model_registry.registry import ModelRegistry
        reg = ModelRegistry()
        record = reg.register(
            model_name="ternary-llama",
            model_version="1.0.0",
            model_type="ternary_student",
            provider="triton",
            architecture="llama",
            parameter_count=15_000_000,
            quantization="ternary",
            compression_ratio=16.0,
            runtime_targets=["cpu", "triton_ternary"],
            parent_model="llama-3-8b",
            artifact_ref="artifact://model/ternary-llama/1.0.0",
        )
        assert record.quantization == "ternary"
        assert record.compression_ratio == 16.0
        assert "triton_ternary" in record.runtime_targets
