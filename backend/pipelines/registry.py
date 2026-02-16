"""Pipeline registry for managing and discovering available pipelines."""

from __future__ import annotations

from typing import Any

from backend.pipelines.base import BasePipeline
from backend.pipelines.crewai_pipeline import CrewAIPipeline
from backend.pipelines.lex_intelligence import create_lex_intelligence_crew


class PipelineRegistry:
    """Central registry for all available AI pipelines."""
    
    def __init__(self):
        """Initialize the pipeline registry."""
        self._pipelines: dict[str, BasePipeline] = {}
        self._register_default_pipelines()
    
    def _register_default_pipelines(self) -> None:
        """Register default pipelines on initialization."""
        # Register Lex Intelligence Ultimate
        lex_pipeline = CrewAIPipeline(
            name="lex_intelligence",
            description="Lex Intelligence Ultimate: 6 agents across 4 LLMs for comprehensive AI analysis",
            crew_factory=create_lex_intelligence_crew,
        )
        self.register(lex_pipeline)
        
        # Register Calculus Intelligence stub
        calculus_pipeline = StubPipeline(
            name="calculus_intelligence",
            description="Calculus Intelligence: Advanced mathematical and analytical reasoning (Coming Soon)",
        )
        self.register(calculus_pipeline)
        
        # Register Forge Intelligence stub
        forge_pipeline = StubPipeline(
            name="forge_intelligence",
            description="Forge Intelligence: Code generation and software engineering (Coming Soon)",
        )
        self.register(forge_pipeline)
    
    def register(self, pipeline: BasePipeline) -> None:
        """Register a pipeline in the registry.
        
        Args:
            pipeline: Pipeline instance to register
        """
        self._pipelines[pipeline.name] = pipeline
    
    def get_pipeline(self, name: str) -> BasePipeline:
        """Get a pipeline by name.
        
        Args:
            name: Pipeline name
            
        Returns:
            Pipeline instance
            
        Raises:
            KeyError: If pipeline not found
        """
        if name not in self._pipelines:
            raise KeyError(f"Pipeline not found: {name}")
        return self._pipelines[name]
    
    def list_pipelines(self) -> list[dict[str, Any]]:
        """List all registered pipelines.
        
        Returns:
            List of pipeline metadata dictionaries
        """
        return [
            pipeline.get_metadata()
            for pipeline in self._pipelines.values()
        ]


class StubPipeline(BasePipeline):
    """Stub pipeline for future implementations."""
    
    def __init__(self, name: str, description: str):
        """Initialize stub pipeline.
        
        Args:
            name: Pipeline name
            description: Pipeline description
        """
        super().__init__(name, description)
    
    async def execute(self, input_data: dict[str, Any], progress_callback=None):
        """Stub execute method that raises NotImplementedError.
        
        Args:
            input_data: Input data
            progress_callback: Progress callback
            
        Raises:
            NotImplementedError: Always raised for stub pipelines
        """
        raise NotImplementedError(f"Pipeline '{self.name}' is not yet implemented")


# Global pipeline registry instance
pipeline_registry = PipelineRegistry()
