"""Tests for pipeline registry."""

import os
import pytest

# Set environment variables before importing
os.environ['OPENAI_API_KEY'] = 'test'
os.environ['ANTHROPIC_API_KEY'] = 'test'
os.environ['GOOGLE_API_KEY'] = 'test'
os.environ['XAI_API_KEY'] = 'test'
os.environ['COURTLISTENER_API_KEY'] = 'test'

from backend.pipelines.registry import get_pipeline, list_pipelines
from backend.pipelines.lex_intelligence import create_lex_intelligence


def test_list_pipelines():
    """Test listing all pipelines."""
    pipelines = list_pipelines()
    
    assert len(pipelines) == 3
    pipeline_names = [p["name"] for p in pipelines]
    assert "lex_intelligence" in pipeline_names
    assert "calculus_intelligence" in pipeline_names
    assert "forge_intelligence" in pipeline_names


def test_get_pipeline_lex():
    """Test getting Lex Intelligence pipeline."""
    pipeline = get_pipeline("lex_intelligence")
    
    assert pipeline.name == "Lex Intelligence Ultimate"
    agents = pipeline.get_agents()
    assert len(agents) == 6


def test_get_pipeline_calculus():
    """Test getting Calculus Intelligence stub."""
    pipeline = get_pipeline("calculus_intelligence")
    
    assert pipeline.name == "Calculus Intelligence"
    assert "coming soon" in pipeline.description.lower()


def test_get_pipeline_forge():
    """Test getting Forge Intelligence stub."""
    pipeline = get_pipeline("forge_intelligence")
    
    assert pipeline.name == "Forge Intelligence"
    assert "coming soon" in pipeline.description.lower()


def test_get_pipeline_invalid():
    """Test getting invalid pipeline raises KeyError."""
    with pytest.raises(KeyError) as exc_info:
        get_pipeline("nonexistent")
    
    assert "not registered" in str(exc_info.value)


def test_pipeline_singleton():
    """Test that pipelines are singletons."""
    pipeline1 = get_pipeline("lex_intelligence")
    pipeline2 = get_pipeline("lex_intelligence")
    
    assert pipeline1 is pipeline2
