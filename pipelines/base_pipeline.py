"""Base pipeline interface with AgentProgress and PipelineResult."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentProgress:
    """Progress update for a single agent."""
    agent_name: str
    agent_role: str
    status: AgentStatus
    model: str = "unknown"
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    input_tokens: int = 0
    output_tokens: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0

    @property
    def duration_ms(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return None

    @property
    def token_summary(self) -> str:
        from pipelines.token_estimator import format_token_summary
        return format_token_summary(
            self.input_tokens, self.output_tokens, self.cost_usd, self.model,
        )


@dataclass
class PipelineResult:
    """Final result from a pipeline execution."""
    pipeline_id: str
    pipeline_name: str
    query: str
    final_output: str
    agent_outputs: list[AgentProgress]
    total_tokens: int
    total_cost_usd: float
    total_duration_ms: float
    success: bool
    error: Optional[str] = None


class BasePipeline(ABC):
    """Abstract base for all pipelines."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(
        self, query: str, user_hash: str, on_progress: callable = None,
    ) -> PipelineResult:
        ...

    @abstractmethod
    def get_agents(self) -> list[dict]:
        ...

    @abstractmethod
    def estimate_cost(self, input_length: int) -> float:
        ...
