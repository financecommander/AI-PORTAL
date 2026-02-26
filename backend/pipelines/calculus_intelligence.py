"""Calculus Intelligence — stub for Phase 2 expansion."""

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult


class CalculusIntelligence(BasePipeline):
    """Stub for Calculus Intelligence pipeline."""
    
    def __init__(self):
        super().__init__(
            name="Calculus Intelligence",
            description="General-purpose deep reasoning engine (coming soon)",
        )

    async def execute(self, query, user_hash, on_progress=None):
        """Execute pipeline (not yet implemented)."""
        raise NotImplementedError("Calculus Intelligence is not yet implemented")

    def get_agents(self):
        """Return list of agents."""
        return [
            {
                "name": "Deep Reasoner",
                "goal": "Complex analytical reasoning",
                "model": "TBD"
            }
        ]

    def estimate_cost(self, input_length):
        """Estimate cost."""
        return 0.0
