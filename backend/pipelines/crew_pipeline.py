"""CrewAI pipeline wrapper with progress tracking and token estimation."""

import asyncio
import time
from typing import Optional, Callable, Any
from crewai import Crew, Agent, Task
from langchain.callbacks.base import BaseCallbackHandler
from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.utils.token_estimator import calculate_cost, estimate_tokens


class ProgressCallback(BaseCallbackHandler):
    """
    Callback handler for CrewAI to track progress and token usage.
    Implements LangChain's callback interface for LLM events.
    """

    def __init__(self, agents: list[Agent], on_progress: Optional[Callable] = None):
        """
        Initialize callback handler.
        
        Args:
            agents: List of agents in the crew
            on_progress: Callback function for progress updates
        """
        super().__init__()
        self.agents = agents
        self.on_progress = on_progress
        self._pending_input_tokens: dict[str, int] = {}
        self._agent_metrics: dict[str, dict] = {}
        self._current_agent: Optional[str] = None
        
        # Initialize metrics for each agent
        for agent in agents:
            agent_name = agent.role
            self._agent_metrics[agent_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "calls": 0
            }

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        **kwargs: Any
    ) -> None:
        """
        Called when LLM starts processing.
        Estimate input tokens and notify progress.
        
        Args:
            serialized: Serialized LLM info
            prompts: Input prompts
            kwargs: Additional arguments
        """
        # Estimate input tokens
        total_input_tokens = sum(estimate_tokens(prompt) for prompt in prompts)
        
        # Store for later use in on_llm_end
        run_id = kwargs.get("run_id", "unknown")
        self._pending_input_tokens[str(run_id)] = total_input_tokens
        
        # Resolve which agent is running
        agent_role = self._resolve_agent_role(kwargs)
        if agent_role:
            self._current_agent = agent_role
            if self.on_progress:
                self.on_progress("agent_start", {
                    "agent": agent_role,
                    "input_tokens": total_input_tokens
                })

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """
        Called when LLM finishes processing.
        Extract token counts and calculate costs.
        
        Args:
            response: LLM response object
            kwargs: Additional arguments
        """
        run_id = str(kwargs.get("run_id", "unknown"))
        agent_role = self._current_agent or self._resolve_agent_role(kwargs)
        
        if not agent_role or agent_role not in self._agent_metrics:
            return
        
        # Get input tokens from pending dict
        input_tokens = self._pending_input_tokens.pop(run_id, 0)
        
        # Extract output tokens from response
        output_tokens = self._extract_output_tokens(response)
        
        # Extract model from response
        model = self._extract_model(response, kwargs)
        
        # Calculate cost
        cost = calculate_cost(model, input_tokens, output_tokens)
        
        # Update agent metrics
        metrics = self._agent_metrics[agent_role]
        metrics["input_tokens"] += input_tokens
        metrics["output_tokens"] += output_tokens
        metrics["cost"] += cost
        metrics["calls"] += 1
        
        # Notify progress
        if self.on_progress:
            self.on_progress("token_update", {
                "agent": agent_role,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "total_tokens": metrics["input_tokens"] + metrics["output_tokens"],
                "total_cost": metrics["cost"]
            })

    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """
        Called when an agent completes its task.
        
        Args:
            finish: Agent finish info
            kwargs: Additional arguments
        """
        if self._current_agent and self.on_progress:
            metrics = self._agent_metrics.get(self._current_agent, {})
            self.on_progress("agent_complete", {
                "agent": self._current_agent,
                "metrics": metrics
            })
        self._current_agent = None

    def _resolve_agent_role(self, kwargs: dict) -> Optional[str]:
        """
        Resolve which agent is currently running.
        
        Args:
            kwargs: Callback kwargs that may contain agent info
        
        Returns:
            Agent role name or None
        """
        # Try to get agent from tags or other metadata
        tags = kwargs.get("tags", [])
        for tag in tags:
            for agent in self.agents:
                if agent.role in tag or tag in agent.role:
                    return agent.role
        
        # Return current agent if set
        return self._current_agent

    def _extract_output_tokens(self, response: Any) -> int:
        """
        Extract output token count from LLM response.
        
        Args:
            response: LLM response object
        
        Returns:
            Output token count
        """
        # Try to extract usage metadata from response
        usage = self._extract_usage_metadata(response)
        if usage and "completion_tokens" in usage:
            return usage["completion_tokens"]
        
        # Fallback: estimate from response text
        if hasattr(response, "generations"):
            text = ""
            for generation_list in response.generations:
                for generation in generation_list:
                    if hasattr(generation, "text"):
                        text += generation.text
            return estimate_tokens(text) if text else 0
        
        return 0

    def _extract_usage_metadata(self, response: Any) -> Optional[dict]:
        """
        Extract usage metadata from provider response.
        
        Args:
            response: LLM response object
        
        Returns:
            Usage dictionary or None
        """
        # OpenAI style
        if hasattr(response, "llm_output") and response.llm_output:
            if "token_usage" in response.llm_output:
                return response.llm_output["token_usage"]
        
        # Anthropic style
        if hasattr(response, "response_metadata"):
            if "usage" in response.response_metadata:
                return response.response_metadata["usage"]
        
        return None

    def _extract_model(self, response: Any, kwargs: dict) -> str:
        """
        Extract model name from response or kwargs.
        
        Args:
            response: LLM response object
            kwargs: Callback kwargs
        
        Returns:
            Model name (defaults to gpt-4o)
        """
        # Try from llm_output
        if hasattr(response, "llm_output") and response.llm_output:
            if "model_name" in response.llm_output:
                return response.llm_output["model_name"]
        
        # Try from invocation_params
        invocation_params = kwargs.get("invocation_params", {})
        if "model" in invocation_params:
            return invocation_params["model"]
        if "model_name" in invocation_params:
            return invocation_params["model_name"]
        
        # Default to gpt-4o
        return "gpt-4o"

    def get_agent_breakdown(self) -> list[dict]:
        """
        Get breakdown of metrics per agent.
        
        Returns:
            List of agent metrics dictionaries
        """
        breakdown = []
        for agent in self.agents:
            agent_name = agent.role
            metrics = self._agent_metrics.get(agent_name, {})
            breakdown.append({
                "agent": agent_name,
                "input_tokens": metrics.get("input_tokens", 0),
                "output_tokens": metrics.get("output_tokens", 0),
                "total_tokens": metrics.get("input_tokens", 0) + metrics.get("output_tokens", 0),
                "cost": metrics.get("cost", 0.0),
                "calls": metrics.get("calls", 0)
            })
        return breakdown

    def get_total_metrics(self) -> dict:
        """
        Get total metrics across all agents.
        
        Returns:
            Total metrics dictionary
        """
        total_input = sum(m.get("input_tokens", 0) for m in self._agent_metrics.values())
        total_output = sum(m.get("output_tokens", 0) for m in self._agent_metrics.values())
        total_cost = sum(m.get("cost", 0.0) for m in self._agent_metrics.values())
        
        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost": total_cost
        }


class CrewPipeline(BasePipeline):
    """
    Wrapper for CrewAI crews to integrate with the pipeline interface.
    Handles async execution and progress tracking.
    """

    def __init__(
        self,
        name: str,
        description: str,
        agents: list[Agent],
        tasks: list[Task],
        verbose: bool = False
    ):
        """
        Initialize CrewAI pipeline wrapper.
        
        Args:
            name: Pipeline name
            description: Pipeline description
            agents: List of CrewAI agents
            tasks: List of CrewAI tasks
            verbose: Enable verbose logging
        """
        super().__init__(name, description)
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose
        self._crew: Optional[Crew] = None

    def _inject_query(self, query: str):
        """
        Inject user query into task descriptions.
        
        Args:
            query: User query to inject
        """
        for task in self.tasks:
            if not task.description.endswith(f"\n\nUser Query: {query}"):
                task.description += f"\n\nUser Query: {query}"

    async def execute(
        self,
        query: str,
        user_hash: str,
        on_progress: Optional[Callable[[str, dict], None]] = None
    ) -> PipelineResult:
        """
        Execute the CrewAI pipeline.
        
        Args:
            query: User query to process
            user_hash: Hashed user identifier
            on_progress: Optional callback for progress updates
        
        Returns:
            PipelineResult with output and metrics
        """
        start_time = time.perf_counter()
        
        # Inject query into tasks
        self._inject_query(query)
        
        # Create progress callback
        callback = ProgressCallback(self.agents, on_progress)
        
        # Create crew with callback
        self._crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=self.verbose,
            callbacks=[callback]
        )
        
        # Execute crew in thread pool (CrewAI is synchronous)
        loop = asyncio.get_event_loop()
        try:
            output = await loop.run_in_executor(
                None,
                self._crew.kickoff
            )
        except Exception as e:
            # Notify error
            if on_progress:
                on_progress("error", {"message": str(e)})
            raise
        
        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Get final metrics
        total_metrics = callback.get_total_metrics()
        agent_breakdown = callback.get_agent_breakdown()
        
        # Notify completion
        if on_progress:
            on_progress("complete", {
                "output": str(output),
                "total_tokens": total_metrics["total_tokens"],
                "total_cost": total_metrics["total_cost"],
                "duration_ms": duration_ms
            })
        
        return PipelineResult(
            output=str(output),
            total_tokens=total_metrics["total_tokens"],
            total_cost=total_metrics["total_cost"],
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={
                "user_hash": user_hash,
                "query": query,
                "verbose": self.verbose
            }
        )

    def get_agents(self) -> list[dict[str, Any]]:
        """Return list of agents in this pipeline."""
        return [
            {
                "name": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory[:100] + "..." if len(agent.backstory) > 100 else agent.backstory,
                "model": getattr(agent.llm, "model_name", "unknown") if agent.llm else "unknown"
            }
            for agent in self.agents
        ]

    def estimate_cost(self, input_length: int) -> float:
        """
        Estimate cost for given input length.
        
        Args:
            input_length: Length of input text
        
        Returns:
            Estimated cost in USD
        """
        # Rough estimate: input_length * number of agents * 2 (for back-and-forth)
        estimated_tokens = estimate_tokens("x" * input_length) * len(self.agents) * 2
        # Use average mid-tier pricing
        return calculate_cost("gpt-4o", estimated_tokens // 2, estimated_tokens // 2)
