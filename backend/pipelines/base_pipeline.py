"""Base pipeline interface for multi-agent pipelines."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, Any


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    output: str
    total_tokens: int
    total_cost: float
    duration_ms: float
    agent_breakdown: list[dict[str, Any]]
    metadata: dict[str, Any]


class BasePipeline(ABC):
    """Abstract base class for all multi-agent pipelines."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(
        self,
        query: str,
        user_hash: str,
        on_progress: Optional[Callable[[str, dict], None]] = None
    ) -> PipelineResult:
        """
        Execute the pipeline with the given query.
        
        Args:
            query: User query to process
            user_hash: Hashed user identifier
            on_progress: Optional callback for progress updates
                        Called with (event_type, data)
        
        Returns:
            PipelineResult with output and metrics
        """
        pass

    @abstractmethod
    def get_agents(self) -> list[dict[str, Any]]:
        """Return list of agents in this pipeline."""
        pass

    @abstractmethod
    def estimate_cost(self, input_length: int) -> float:
        """Estimate cost for given input length."""
        pass
