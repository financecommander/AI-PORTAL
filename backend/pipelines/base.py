"""Base pipeline interface for AI agent orchestration.

Provides the foundational classes for building multi-agent pipelines.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class AgentStatus(Enum):
    """Status of an agent during pipeline execution."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentProgress:
    """Progress update from an agent during execution."""
    
    agent_name: str
    status: AgentStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> float:
        """Calculate duration in milliseconds if start time is in metadata."""
        if "start_time" in self.metadata:
            start = self.metadata["start_time"]
            if isinstance(start, datetime):
                delta = self.timestamp - start
                return delta.total_seconds() * 1000
        return 0.0
    
    @property
    def token_summary(self) -> dict[str, int]:
        """Extract token usage from metadata if available."""
        tokens = {}
        if "input_tokens" in self.metadata:
            tokens["input"] = self.metadata["input_tokens"]
        if "output_tokens" in self.metadata:
            tokens["output"] = self.metadata["output_tokens"]
        return tokens


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution."""
    
    pipeline_name: str
    status: str
    output: str
    agents_executed: list[str]
    total_duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    
    @property
    def success(self) -> bool:
        """Whether the pipeline completed successfully."""
        return self.status == "completed" and self.error is None


class BasePipeline(ABC):
    """Abstract base class for all AI pipelines.
    
    Cannot be instantiated directly - subclasses must implement execute().
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(
        self,
        input_data: dict[str, Any],
        progress_callback: Callable[[AgentProgress], None] | None = None,
    ) -> PipelineResult:
        """Execute the pipeline with the given input.
        
        Args:
            input_data: Input parameters for the pipeline
            progress_callback: Optional callback for progress updates
            
        Returns:
            PipelineResult with execution details
        """
        pass
    
    def get_metadata(self) -> dict[str, Any]:
        """Get pipeline metadata for listing/discovery."""
        return {
            "name": self.name,
            "description": self.description,
        }
