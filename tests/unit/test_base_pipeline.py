"""Tests for the base pipeline interface, AgentProgress, and PipelineResult."""

import pytest

from pipelines.base_pipeline import (
    AgentProgress,
    AgentStatus,
    BasePipeline,
    PipelineResult,
)
from pipelines.token_estimator import estimate_pipeline_cost, format_token_summary


# ---------------------------------------------------------------------------
# AgentStatus
# ---------------------------------------------------------------------------


class TestAgentStatus:
    def test_values(self):
        assert AgentStatus.PENDING == "pending"
        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.COMPLETED == "completed"
        assert AgentStatus.FAILED == "failed"

    def test_is_str_enum(self):
        assert isinstance(AgentStatus.PENDING, str)


# ---------------------------------------------------------------------------
# AgentProgress
# ---------------------------------------------------------------------------


class TestAgentProgress:
    def test_defaults(self):
        ap = AgentProgress(
            agent_name="analyst",
            agent_role="Financial Analyst",
            status=AgentStatus.PENDING,
        )
        assert ap.model == "unknown"
        assert ap.output is None
        assert ap.error is None
        assert ap.started_at is None
        assert ap.completed_at is None
        assert ap.input_tokens == 0
        assert ap.output_tokens == 0
        assert ap.tokens_used == 0
        assert ap.cost_usd == 0.0

    def test_duration_ms(self):
        ap = AgentProgress(
            agent_name="analyst",
            agent_role="Financial Analyst",
            status=AgentStatus.COMPLETED,
            started_at=1000.0,
            completed_at=1002.5,
        )
        assert ap.duration_ms == 2500.0

    def test_duration_ms_none_when_not_started(self):
        ap = AgentProgress(
            agent_name="analyst",
            agent_role="Financial Analyst",
            status=AgentStatus.PENDING,
        )
        assert ap.duration_ms is None

    def test_duration_ms_none_when_not_completed(self):
        ap = AgentProgress(
            agent_name="analyst",
            agent_role="Financial Analyst",
            status=AgentStatus.RUNNING,
            started_at=1000.0,
        )
        assert ap.duration_ms is None

    def test_token_summary(self):
        ap = AgentProgress(
            agent_name="analyst",
            agent_role="Financial Analyst",
            status=AgentStatus.COMPLETED,
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
        )
        summary = ap.token_summary
        assert "gpt-4o" in summary
        assert "150" in summary
        assert "100" in summary
        assert "50" in summary
        assert "$0.0010" in summary

    def test_failed_status_with_error(self):
        ap = AgentProgress(
            agent_name="analyst",
            agent_role="Financial Analyst",
            status=AgentStatus.FAILED,
            error="API timeout",
        )
        assert ap.status == AgentStatus.FAILED
        assert ap.error == "API timeout"


# ---------------------------------------------------------------------------
# PipelineResult
# ---------------------------------------------------------------------------


class TestPipelineResult:
    def test_successful_result(self):
        agents = [
            AgentProgress(
                agent_name="agent1",
                agent_role="role1",
                status=AgentStatus.COMPLETED,
            ),
        ]
        result = PipelineResult(
            pipeline_id="test-123",
            pipeline_name="Test Pipeline",
            query="What is revenue?",
            final_output="Revenue is income.",
            agent_outputs=agents,
            total_tokens=200,
            total_cost_usd=0.005,
            total_duration_ms=1500.0,
            success=True,
        )
        assert result.success is True
        assert result.error is None
        assert result.pipeline_id == "test-123"
        assert result.pipeline_name == "Test Pipeline"
        assert len(result.agent_outputs) == 1

    def test_failed_result(self):
        result = PipelineResult(
            pipeline_id="test-456",
            pipeline_name="Test Pipeline",
            query="broken query",
            final_output="",
            agent_outputs=[],
            total_tokens=0,
            total_cost_usd=0.0,
            total_duration_ms=100.0,
            success=False,
            error="Pipeline execution failed",
        )
        assert result.success is False
        assert result.error == "Pipeline execution failed"


# ---------------------------------------------------------------------------
# BasePipeline (abstract)
# ---------------------------------------------------------------------------


class TestBasePipeline:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BasePipeline("test", "test description")

    def test_concrete_subclass(self):
        class ConcretePipeline(BasePipeline):
            async def execute(self, query, user_hash, on_progress=None):
                return PipelineResult(
                    pipeline_id="id",
                    pipeline_name=self.name,
                    query=query,
                    final_output="done",
                    agent_outputs=[],
                    total_tokens=0,
                    total_cost_usd=0.0,
                    total_duration_ms=0.0,
                    success=True,
                )

            def get_agents(self):
                return [{"name": "agent1", "role": "role1"}]

            def estimate_cost(self, input_length):
                return 0.001

        pipeline = ConcretePipeline("test", "test pipeline")
        assert pipeline.name == "test"
        assert pipeline.description == "test pipeline"
        assert pipeline.get_agents() == [{"name": "agent1", "role": "role1"}]
        assert pipeline.estimate_cost(100) == 0.001


# ---------------------------------------------------------------------------
# Token estimator
# ---------------------------------------------------------------------------


class TestTokenEstimator:
    def test_format_token_summary(self):
        summary = format_token_summary(100, 50, 0.001, "gpt-4o")
        assert "gpt-4o" in summary
        assert "150" in summary
        assert "100" in summary
        assert "50" in summary

    def test_format_token_summary_large_numbers(self):
        summary = format_token_summary(1_000_000, 500_000, 12.50, "claude-3-opus")
        assert "claude-3-opus" in summary
        assert "1,500,000" in summary
        assert "$12.5000" in summary

    def test_estimate_pipeline_cost_known_model(self):
        cost = estimate_pipeline_cost("gpt-4o", 1_000_000, 1_000_000)
        assert cost == pytest.approx(12.50)

    def test_estimate_pipeline_cost_unknown_model(self):
        cost = estimate_pipeline_cost("unknown-model", 1000, 1000)
        assert cost == 0.0
