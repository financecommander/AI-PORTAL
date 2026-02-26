"""Forge Intelligence — stub for Phase 2 expansion."""

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult


class ForgeIntelligence(BasePipeline):
    """Stub for Forge Intelligence pipeline."""
    
    def __init__(self):
        super().__init__(
            name="Forge Intelligence",
            description="Code generation and software engineering pipeline (coming soon)",
        )

    async def execute(self, query, user_hash, on_progress=None):
        """Execute pipeline (not yet implemented)."""
        raise NotImplementedError("Forge Intelligence is not yet implemented")

    def get_agents(self):
        """Return list of agents."""
        return [
            {
                "name": "Code Architect",
                "goal": "Software design and code generation",
                "model": "TBD"
            }
        ]

    def estimate_cost(self, input_length):
        """Estimate cost."""
        return 0.0
