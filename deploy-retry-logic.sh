#!/bin/bash
set -e
cd /workspaces/AI-PORTAL 2>/dev/null || cd ~/AI-PORTAL 2>/dev/null || { echo "❌"; exit 1; }
mkdir -p 'backend/pipelines'
cat > 'backend/pipelines/crew_pipeline.py' << 'FILEEOF_crew'
"""CrewAI pipeline wrapper with progress tracking and token tracking."""

import asyncio
import time
import inspect
import logging
from typing import Optional, Callable, Any, Union
from crewai import Crew, Agent, Task
from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.utils.token_estimator import calculate_cost, estimate_tokens

logger = logging.getLogger(__name__)


class CrewPipeline(BasePipeline):
    """
    Wrapper for CrewAI crews to integrate with the pipeline interface.
    
    Token tracking uses CrewOutput.token_usage (populated by CrewAI/LiteLLM)
    rather than langchain callbacks, which don't fire with modern CrewAI.
    """

    def __init__(
        self,
        name: str,
        description: str,
        agents: list[Agent],
        tasks: list[Task],
        verbose: bool = False
    ):
        super().__init__(name, description)
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose
        self._crew: Optional[Crew] = None

    def _inject_query(self, query: str):
        """Inject user query into task descriptions, replacing any previous query."""
        marker = "\n\nUser Query: "
        for task in self.tasks:
            # Strip any previously injected query first
            idx = task.description.find(marker)
            if idx != -1:
                task.description = task.description[:idx]
            task.description += f"{marker}{query}"

    def _extract_token_usage(self, output: Any) -> dict:
        """
        Extract token usage from CrewOutput object.
        
        CrewAI populates token_usage via LiteLLM's internal tracking.
        Returns dict with total_tokens, prompt_tokens, completion_tokens.
        """
        usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
        }
        
        token_usage = getattr(output, "token_usage", None)
        if token_usage:
            if hasattr(token_usage, "model_dump"):
                usage_data = token_usage.model_dump()
            elif hasattr(token_usage, "dict"):
                usage_data = token_usage.dict()
            elif isinstance(token_usage, dict):
                usage_data = token_usage
            else:
                usage_data = {}
            
            usage["total_tokens"] = usage_data.get("total_tokens", 0)
            usage["prompt_tokens"] = usage_data.get("prompt_tokens", 0)
            usage["completion_tokens"] = usage_data.get("completion_tokens", 0)
            usage["successful_requests"] = usage_data.get("successful_requests", 0)
        
        return usage

    def _build_agent_breakdown(self, output: Any, total_usage: dict) -> list[dict]:
        """
        Build per-agent token breakdown.
        
        If CrewOutput has tasks_output with per-task data, use that.
        Otherwise, estimate proportionally from output lengths.
        """
        breakdown = []
        tasks_output = getattr(output, "tasks_output", [])
        
        agent_outputs = {}
        for i, agent in enumerate(self.agents):
            agent_name = agent.role
            task_text = ""
            if i < len(tasks_output):
                task_out = tasks_output[i]
                task_text = getattr(task_out, "raw", "") or str(task_out)
            agent_outputs[agent_name] = task_text
        
        total_output_len = sum(len(t) for t in agent_outputs.values()) or 1
        total_tokens = total_usage.get("total_tokens", 0)
        prompt_tokens = total_usage.get("prompt_tokens", 0)
        completion_tokens = total_usage.get("completion_tokens", 0)
        
        for agent in self.agents:
            agent_name = agent.role
            text = agent_outputs.get(agent_name, "")
            proportion = len(text) / total_output_len if total_output_len > 0 else 1 / max(len(self.agents), 1)
            
            agent_input = int(prompt_tokens * proportion)
            agent_output = int(completion_tokens * proportion)
            agent_total = agent_input + agent_output
            
            model = self._get_agent_model(agent)
            agent_cost = calculate_cost(model, agent_input, agent_output)
            
            breakdown.append({
                "agent": agent_name,
                "input_tokens": agent_input,
                "output_tokens": agent_output,
                "total_tokens": agent_total,
                "cost": round(agent_cost, 6),
                "calls": 1,
                "model": model,
            })
        
        return breakdown

    def _get_agent_model(self, agent: Agent) -> str:
        """Extract model name from agent's LLM for cost calculation."""
        llm = agent.llm
        if llm is None:
            return "gpt-4o"
        
        if hasattr(llm, "model"):
            model = llm.model
            for prefix in ("gemini/", "xai/", "anthropic/", "openai/"):
                if model.startswith(prefix):
                    model = model[len(prefix):]
            return model
        
        if hasattr(llm, "model_name"):
            model = llm.model_name
            for prefix in ("xai/",):
                if model.startswith(prefix):
                    model = model[len(prefix):]
            return model
        
        return "gpt-4o"

    async def execute(
        self,
        query: str,
        user_hash: str,
        on_progress: Optional[Callable[[str, dict], None]] = None
    ) -> PipelineResult:
        """Execute the CrewAI pipeline."""
        start_time = time.perf_counter()
        
        self._inject_query(query)
        
        # Track per-agent timing
        agent_start_times: dict[str, float] = {}
        completed_count = 0
        loop = asyncio.get_event_loop()

        def _send_event_sync(event_type: str, data: dict):
            """Bridge sync callback -> async WebSocket event."""
            if on_progress:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        on_progress(event_type, data), loop
                    )
                    future.result(timeout=5)
                except Exception:
                    pass

        def task_callback(task_output):
            """Called by CrewAI after each task completes."""
            nonlocal completed_count
            
            # Determine which agent just completed
            agent_name = None
            if hasattr(task_output, 'agent') and task_output.agent:
                agent_name = str(task_output.agent)
            elif completed_count < len(self.agents):
                agent_name = self.agents[completed_count].role
            
            if agent_name:
                duration = (time.perf_counter() - agent_start_times.get(agent_name, start_time)) * 1000
                raw_output = getattr(task_output, 'raw', '') or str(task_output)
                
                _send_event_sync("agent_complete", {
                    "agent": agent_name,
                    "duration_ms": round(duration, 1),
                    "output": raw_output[:500],  # Truncate for WS
                })
            
            completed_count += 1
            
            # Signal next agent starting
            if completed_count < len(self.agents):
                next_agent = self.agents[completed_count].role
                agent_start_times[next_agent] = time.perf_counter()
                _send_event_sync("agent_start", {"agent": next_agent})
        
        self._crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=self.verbose,
            task_callback=task_callback,
        )
        
        if on_progress:
            try:
                await on_progress("pipeline_start", {
                    "agents": [a.role for a in self.agents],
                    "query": query,
                })
            except Exception:
                pass
        
        # Signal first agent starting
        if self.agents and on_progress:
            first_agent = self.agents[0].role
            agent_start_times[first_agent] = time.perf_counter()
            try:
                await on_progress("agent_start", {"agent": first_agent})
            except Exception:
                pass
        
        output = None
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # Re-inject query on retry (task descriptions were already cleaned)
                if attempt > 0:
                    logger.warning(f"Pipeline retry {attempt}/{max_retries} after connection error")
                    self._inject_query(query)
                    # Rebuild crew to reset internal state
                    self._crew = Crew(
                        agents=self.agents,
                        tasks=self.tasks,
                        verbose=self.verbose,
                        task_callback=task_callback,
                    )
                    # Reset agent tracking for retry
                    completed_count = 0
                    agent_start_times.clear()
                    if self.agents and on_progress:
                        first_agent = self.agents[0].role
                        agent_start_times[first_agent] = time.perf_counter()
                        try:
                            await on_progress("agent_start", {"agent": first_agent})
                        except Exception:
                            pass

                output = await loop.run_in_executor(None, self._crew.kickoff)
                break  # Success — exit retry loop

            except Exception as e:
                error_msg = str(e).lower()
                is_retryable = any(phrase in error_msg for phrase in [
                    "incomplete chunked read",
                    "peer closed connection",
                    "connection reset",
                    "connection aborted",
                    "read timed out",
                    "remotedisconnected",
                    "server disconnected",
                ])

                if is_retryable and attempt < max_retries:
                    wait_seconds = 3 * (attempt + 1)
                    logger.warning(
                        f"Retryable error on attempt {attempt + 1}: {e}. "
                        f"Waiting {wait_seconds}s before retry."
                    )
                    if on_progress:
                        try:
                            await on_progress("retry", {
                                "attempt": attempt + 1,
                                "max_retries": max_retries,
                                "reason": str(e)[:200],
                            })
                        except Exception:
                            pass
                    await asyncio.sleep(wait_seconds)
                    continue

                # Non-retryable or exhausted retries
                duration_ms = (time.perf_counter() - start_time) * 1000
                partial_usage = self._extract_token_usage(output) if output else {
                    "total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0,
                }
                if partial_usage.get("total_tokens", 0) > 0:
                    logger.warning(
                        f"Pipeline failed after consuming {partial_usage['total_tokens']} tokens "
                        f"in {duration_ms:.0f}ms"
                    )
                if on_progress:
                    try:
                        await on_progress("error", {
                            "message": str(e),
                            "partial_tokens": partial_usage.get("total_tokens", 0),
                            "attempts": attempt + 1,
                        })
                    except Exception:
                        pass
                raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        total_usage = self._extract_token_usage(output)
        agent_breakdown = self._build_agent_breakdown(output, total_usage)
        
        total_cost = sum(a["cost"] for a in agent_breakdown)
        total_tokens = total_usage.get("total_tokens", 0)
        
        logger.info(
            f"Pipeline completed: {total_tokens} tokens, ${total_cost:.4f}, "
            f"{duration_ms:.0f}ms, {total_usage.get('successful_requests', 0)} API calls"
        )
        
        # Note: 'complete' event is sent by the route handler with full agent_breakdown
        
        return PipelineResult(
            output=str(output),
            total_tokens=total_tokens,
            total_cost=round(total_cost, 6),
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={
                "user_hash": user_hash,
                "query": query,
                "successful_requests": total_usage.get("successful_requests", 0),
                "prompt_tokens": total_usage.get("prompt_tokens", 0),
                "completion_tokens": total_usage.get("completion_tokens", 0),
            }
        )

    def get_agents(self) -> list[dict[str, Any]]:
        """Return list of agents in this pipeline."""
        return [
            {
                "name": agent.role,
                "goal": agent.goal,
                "backstory": agent.backstory[:100] + "..." if len(agent.backstory) > 100 else agent.backstory,
                "model": self._get_agent_model(agent),
            }
            for agent in self.agents
        ]

    def estimate_cost(self, input_length: int) -> float:
        """Estimate cost for given input length."""
        estimated_tokens = estimate_tokens("x" * input_length) * len(self.agents) * 2
        return calculate_cost("gpt-4o", estimated_tokens // 2, estimated_tokens // 2)

FILEEOF_crew
echo "✅ crew_pipeline.py updated with retry logic"
git add -A
git commit --no-gpg-sign -m "feat: auto-retry pipeline on connection drops (2 retries, exponential backoff)

Retries on: incomplete chunked read, peer closed connection, connection reset,
read timed out, remote disconnected. Waits 3s then 6s between retries.
Rebuilds Crew instance on retry to reset internal state.
Sends 'retry' event to frontend WebSocket for UI feedback.
Non-retryable errors fail immediately as before." || echo "Nothing"
git push origin main
echo "✅ Pushed. Backend rebuild:"
echo "  cd ~/AI-PORTAL && git fetch origin main && git reset --hard origin/main"
echo "  sudo docker compose -f docker-compose.v2.yml build --no-cache backend"
echo "  sudo docker compose -f docker-compose.v2.yml up -d --force-recreate"
