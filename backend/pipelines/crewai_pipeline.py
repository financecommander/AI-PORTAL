"""CrewAI pipeline wrapper with async execution and progress tracking."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable

from backend.pipelines.base import (
    AgentProgress,
    AgentStatus,
    BasePipeline,
    PipelineResult,
)


class CrewAIPipeline(BasePipeline):
    """Wrapper for CrewAI multi-agent workflows with progress callbacks.
    
    Provides async execution and real-time progress updates for CrewAI crews.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        crew_factory: Callable[[], Any],  # Returns a CrewAI Crew instance
    ):
        """Initialize the CrewAI pipeline wrapper.
        
        Args:
            name: Pipeline name
            description: Pipeline description
            crew_factory: Callable that returns a configured CrewAI Crew
        """
        super().__init__(name, description)
        self.crew_factory = crew_factory
    
    async def execute(
        self,
        input_data: dict[str, Any],
        progress_callback: Callable[[AgentProgress], None] | None = None,
    ) -> PipelineResult:
        """Execute the CrewAI pipeline asynchronously.
        
        Args:
            input_data: Input parameters for the crew (passed as kwargs)
            progress_callback: Optional callback for progress updates
            
        Returns:
            PipelineResult with execution details
        """
        start_time = datetime.now()
        agents_executed = []
        
        try:
            # Create the crew
            crew = self.crew_factory()
            
            # Extract agent names if available
            if hasattr(crew, 'agents'):
                agents_executed = [agent.role for agent in crew.agents]
            
            # Send initial progress
            if progress_callback:
                for agent_name in agents_executed:
                    progress_callback(
                        AgentProgress(
                            agent_name=agent_name,
                            status=AgentStatus.PENDING,
                            message=f"Queued {agent_name}",
                            metadata={"start_time": start_time},
                        )
                    )
            
            # Execute crew in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: crew.kickoff(inputs=input_data),
            )
            
            # Send completion progress
            if progress_callback:
                for agent_name in agents_executed:
                    progress_callback(
                        AgentProgress(
                            agent_name=agent_name,
                            status=AgentStatus.COMPLETED,
                            message=f"Completed {agent_name}",
                            metadata={"start_time": start_time},
                        )
                    )
            
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Extract output
            output = str(result) if result else "No output"
            
            return PipelineResult(
                pipeline_name=self.name,
                status="completed",
                output=output,
                agents_executed=agents_executed,
                total_duration_ms=duration_ms,
                metadata={
                    "crew_agents": len(agents_executed),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                },
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Send failure progress
            if progress_callback and agents_executed:
                progress_callback(
                    AgentProgress(
                        agent_name=agents_executed[-1] if agents_executed else "unknown",
                        status=AgentStatus.FAILED,
                        message=f"Pipeline failed: {str(e)}",
                        metadata={"start_time": start_time},
                    )
                )
            
            return PipelineResult(
                pipeline_name=self.name,
                status="failed",
                output="",
                agents_executed=agents_executed,
                total_duration_ms=duration_ms,
                error=str(e),
                metadata={
                    "error_type": type(e).__name__,
                },
            )
