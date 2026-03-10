"""Base pipeline interface for multi-agent pipelines."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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


@dataclass
class PipelineContext:
    """Shared context passed between pipeline agents (Swarm pattern).

    Replaces ad-hoc string concatenation with structured state that
    flows through every agent in the pipeline.

    Attributes:
        query: Original user query.
        agent_outputs: Full untruncated text output per agent.
        structured_data: Typed data (lists, dicts) shared between agents.
        errors: Per-agent error records.
        routing: Skip/branch instructions set by agents at runtime.
    """
    query: str
    agent_outputs: dict[str, str] = field(default_factory=dict)
    structured_data: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    routing: dict[str, Any] = field(default_factory=dict)

    def set_output(self, agent_name: str, output: str):
        """Store an agent's full output text."""
        self.agent_outputs[agent_name] = output

    def get_output(self, agent_name: str) -> str:
        """Retrieve an agent's output (empty string if not yet produced)."""
        return self.agent_outputs.get(agent_name, "")

    def should_skip(self, agent_name: str) -> bool:
        """Check if an agent should be skipped based on routing decisions."""
        if self.routing.get("skip_all"):
            return True
        return agent_name in self.routing.get("skip_agents", [])

    def skip_remaining(self):
        """Signal that all remaining agents should be skipped."""
        self.routing["skip_all"] = True

    def skip_agent(self, agent_name: str):
        """Mark a specific agent to be skipped."""
        self.routing.setdefault("skip_agents", []).append(agent_name)


class BasePipeline(ABC):
    """Abstract base class for all multi-agent pipelines."""

    def __init__(self, name: str, description: str, category: str = "general"):
        self.name = name
        self.description = description
        self.category = category

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

    async def _run_agent(
        self,
        agent_name: str,
        provider: BaseProvider,
        context: PipelineContext,
        build_messages: Callable[["PipelineContext"], list[dict]],
        model: str,
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 3000,
        on_progress: Optional[Callable] = None,
    ) -> tuple[str, dict]:
        """Run an agent with Swarm-style context management.

        Higher-level wrapper around ``_stream_agent_response`` that:
        1. Checks ``context.should_skip()`` — emits ``agent_skip`` if true.
        2. Builds messages from context via ``build_messages`` callback.
        3. Delegates to ``_stream_agent_response`` for streaming + tokens.
        4. Stores the output in ``context.agent_outputs[agent_name]``.

        Args:
            agent_name: Display name of the agent.
            provider: LLM provider instance.
            context: Shared pipeline context.
            build_messages: Callable that takes context and returns messages list.
            model: Model ID.
            system_prompt: System prompt for the agent.
            temperature: Sampling temperature.
            max_tokens: Max output tokens.
            on_progress: Callback for streaming events.

        Returns:
            Tuple of (output_text, token_dict).
        """
        zero_tokens = {"input": 0, "output": 0, "cost": 0}

        # Conditional routing: skip if flagged
        if context.should_skip(agent_name):
            logger.info("Agent '%s' skipped by routing", agent_name)
            if on_progress:
                await on_progress("agent_start", {"agent": agent_name})
                await on_progress("agent_complete", {
                    "agent": agent_name,
                    "duration_ms": 0,
                    "output": "[Skipped]",
                    "skipped": True,
                })
            context.set_output(agent_name, "")
            return "", zero_tokens

        messages = build_messages(context)
        output, token_dict = await self._stream_agent_response(
            agent_name=agent_name,
            provider=provider,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            on_progress=on_progress,
        )
        context.set_output(agent_name, output)
        return output, token_dict

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

        if not final_chunk:
            logger.warning(
                "Agent '%s' stream ended without a final chunk — "
                "token/cost metrics will be zero", agent_name,
            )

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
