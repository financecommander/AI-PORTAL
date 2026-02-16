"""Tests for base pipeline components.

Tests AgentProgress, PipelineResult, AgentStatus, and BasePipeline.
"""

from datetime import datetime, timedelta

import pytest

from backend.pipelines.base import (
    AgentProgress,
    AgentStatus,
    BasePipeline,
    PipelineResult,
)


class TestAgentProgress:
    """Tests for AgentProgress dataclass."""
    
    def test_duration_ms_with_start_time(self):
        """Test duration_ms property calculates correctly with start_time in metadata."""
        start_time = datetime.now()
        end_time = start_time + timedelta(milliseconds=500)
        
        progress = AgentProgress(
            agent_name="test_agent",
            status=AgentStatus.COMPLETED,
            message="Task complete",
            timestamp=end_time,
            metadata={"start_time": start_time},
        )
        
        # Should be approximately 500ms
        assert 490 <= progress.duration_ms <= 510
    
    def test_duration_ms_without_start_time(self):
        """Test duration_ms returns 0 when no start_time in metadata."""
        progress = AgentProgress(
            agent_name="test_agent",
            status=AgentStatus.RUNNING,
            message="In progress",
        )
        
        assert progress.duration_ms == 0.0
    
    def test_token_summary_with_tokens(self):
        """Test token_summary extracts input and output tokens from metadata."""
        progress = AgentProgress(
            agent_name="test_agent",
            status=AgentStatus.COMPLETED,
            message="Done",
            metadata={
                "input_tokens": 100,
                "output_tokens": 250,
            },
        )
        
        summary = progress.token_summary
        assert summary == {"input": 100, "output": 250}
    
    def test_token_summary_without_tokens(self):
        """Test token_summary returns empty dict when no token info."""
        progress = AgentProgress(
            agent_name="test_agent",
            status=AgentStatus.PENDING,
            message="Queued",
        )
        
        assert progress.token_summary == {}


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""
    
    def test_creation_with_all_fields(self):
        """Test PipelineResult can be created with all fields."""
        result = PipelineResult(
            pipeline_name="test_pipeline",
            status="completed",
            output="Success output",
            agents_executed=["agent1", "agent2"],
            total_duration_ms=1500.0,
            metadata={"key": "value"},
            error=None,
        )
        
        assert result.pipeline_name == "test_pipeline"
        assert result.status == "completed"
        assert result.output == "Success output"
        assert result.agents_executed == ["agent1", "agent2"]
        assert result.total_duration_ms == 1500.0
        assert result.metadata == {"key": "value"}
        assert result.error is None
    
    def test_success_property_true(self):
        """Test success property returns True for completed status without error."""
        result = PipelineResult(
            pipeline_name="test",
            status="completed",
            output="Done",
            agents_executed=[],
            total_duration_ms=100.0,
        )
        
        assert result.success is True
    
    def test_success_property_false_with_error(self):
        """Test success property returns False when error is present."""
        result = PipelineResult(
            pipeline_name="test",
            status="completed",
            output="",
            agents_executed=[],
            total_duration_ms=100.0,
            error="Something went wrong",
        )
        
        assert result.success is False
    
    def test_success_property_false_with_failed_status(self):
        """Test success property returns False for failed status."""
        result = PipelineResult(
            pipeline_name="test",
            status="failed",
            output="",
            agents_executed=[],
            total_duration_ms=100.0,
        )
        
        assert result.success is False


class TestAgentStatus:
    """Tests for AgentStatus enum."""
    
    def test_enum_values(self):
        """Test AgentStatus enum has correct values."""
        assert AgentStatus.PENDING.value == "pending"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.FAILED.value == "failed"
    
    def test_enum_membership(self):
        """Test enum members are accessible."""
        assert hasattr(AgentStatus, "PENDING")
        assert hasattr(AgentStatus, "RUNNING")
        assert hasattr(AgentStatus, "COMPLETED")
        assert hasattr(AgentStatus, "FAILED")


class TestBasePipeline:
    """Tests for BasePipeline abstract class."""
    
    def test_cannot_instantiate_directly(self):
        """Test BasePipeline cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BasePipeline(name="test", description="test description")
    
    def test_can_subclass(self):
        """Test BasePipeline can be subclassed."""
        
        class ConcretePipeline(BasePipeline):
            async def execute(self, input_data, progress_callback=None):
                return PipelineResult(
                    pipeline_name=self.name,
                    status="completed",
                    output="test",
                    agents_executed=[],
                    total_duration_ms=0.0,
                )
        
        # Should not raise an error
        pipeline = ConcretePipeline(name="concrete", description="A concrete pipeline")
        assert pipeline.name == "concrete"
        assert pipeline.description == "A concrete pipeline"
