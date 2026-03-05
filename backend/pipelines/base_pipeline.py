"""Base pipeline interface for multi-agent pipelines."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, Any

from backend.providers.base import BaseProvider

logger = logging.getLogger(__name__)


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
            on_progress: Optional callback for progress updates.
                        Event types: pipeline_start, agent_start,
                        agent_token (live text), agent_complete, complete, error

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

    async def _stream_agent_response(
        self,
        agent_name: str,
        provider: BaseProvider,
        messages: list[dict],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 3000,
        system_prompt: Optional[str] = None,
        on_progress: Optional[Callable] = None,
    ) -> tuple[str, dict]:
        """Stream an agent's LLM response with token-by-token progress events.

        Replaces the pattern:
            response = await provider.send_message(...)
            return response.content, {"input": ..., "output": ..., "cost": ...}

        With streaming that emits ``agent_token`` events via ``on_progress``,
        giving the frontend live text updates for each pipeline agent.

        Args:
            agent_name: Display name of the agent (for progress events).
            provider: LLM provider instance.
            messages: Message list for the LLM.
            model: Model ID to use.
            temperature: Sampling temperature.
            max_tokens: Max output tokens.
            system_prompt: Optional system prompt.
            on_progress: Callback for streaming events.

        Returns:
            Tuple of (full_content, token_dict) where token_dict has
            keys: input, output, cost.
        """
        full_content = ""
        final_chunk = None

        async for chunk in provider.stream_message(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        ):
            full_content += chunk.content
            # Emit live text to frontend
            if on_progress and chunk.content:
                await on_progress("agent_token", {
                    "agent": agent_name,
                    "content": chunk.content,
                })
            if chunk.is_final:
                final_chunk = chunk

        token_dict = {
            "input": final_chunk.input_tokens if final_chunk else 0,
            "output": final_chunk.output_tokens if final_chunk else 0,
            "cost": final_chunk.cost_usd if final_chunk else 0,
        }

        # Save training data for this agent's output
        try:
            from backend.database import engine
            from backend.models import TrainingData
            from sqlmodel import Session

            user_input = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    user_input = m.get("content", "")[:4000]
                    break

            with Session(engine) as session:
                row = TrainingData(
                    pipeline_name=self.name,
                    agent_name=agent_name,
                    model_used=model,
                    system_prompt=(system_prompt or "")[:4000],
                    user_input=user_input,
                    assistant_output=full_content[:8000],
                    input_tokens=token_dict["input"],
                    output_tokens=token_dict["output"],
                    cost_usd=token_dict["cost"],
                )
                session.add(row)
                session.commit()
        except Exception as e:
            logger.warning("Failed to save training data for %s: %s", agent_name, e)

        return full_content, token_dict
