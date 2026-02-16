"""Tests for pipeline registry.

Tests pipeline registration, retrieval, and listing functionality.
"""

import pytest

from backend.pipelines.registry import PipelineRegistry, StubPipeline


@pytest.fixture
def registry():
    """Provide a fresh PipelineRegistry instance for each test."""
    return PipelineRegistry()


class TestPipelineRegistry:
    """Tests for PipelineRegistry class."""
    
    def test_list_pipelines_returns_all_registered(self, registry):
        """Test list_pipelines returns all registered pipelines."""
        pipelines = registry.list_pipelines()
        
        # Should have 3 default pipelines
        assert len(pipelines) == 3
        
        # Extract pipeline names
        names = [p["name"] for p in pipelines]
        assert "lex_intelligence" in names
        assert "calculus_intelligence" in names
        assert "forge_intelligence" in names
    
    def test_get_pipeline_returns_lex_intelligence(self, registry):
        """Test get_pipeline returns Lex Intelligence pipeline."""
        pipeline = registry.get_pipeline("lex_intelligence")
        
        assert pipeline is not None
        assert pipeline.name == "lex_intelligence"
        assert "Lex Intelligence Ultimate" in pipeline.description
    
    def test_get_pipeline_unknown_name_raises_key_error(self, registry):
        """Test get_pipeline raises KeyError for unknown pipeline."""
        with pytest.raises(KeyError, match="Pipeline not found: nonexistent"):
            registry.get_pipeline("nonexistent")
    
    def test_calculus_and_forge_stubs_raise_not_implemented(self, registry):
        """Test Calculus and Forge stub pipelines raise NotImplementedError."""
        import asyncio
        
        # Get Calculus pipeline
        calculus = registry.get_pipeline("calculus_intelligence")
        assert isinstance(calculus, StubPipeline)
        
        # Try to execute - should raise NotImplementedError
        with pytest.raises(NotImplementedError, match="calculus_intelligence.*not yet implemented"):
            asyncio.run(calculus.execute({"input": "test"}))
        
        # Get Forge pipeline
        forge = registry.get_pipeline("forge_intelligence")
        assert isinstance(forge, StubPipeline)
        
        # Try to execute - should raise NotImplementedError
        with pytest.raises(NotImplementedError, match="forge_intelligence.*not yet implemented"):
            asyncio.run(forge.execute({"input": "test"}))
