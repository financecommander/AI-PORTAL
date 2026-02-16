"""Integration tests for pipeline API routes.

Tests GET /pipelines/list, POST /pipelines/run, and authentication.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.pipelines.base import PipelineResult
from backend.routes.pipelines import router, verify_token


@pytest.fixture
def app():
    """Create a FastAPI app with pipeline routes."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def authenticated_app(app):
    """Create an app with authentication dependency overridden."""
    async def mock_verify_token():
        return {"user": "test_user"}
    
    app.dependency_overrides[verify_token] = mock_verify_token
    return app


@pytest.fixture
def authenticated_client(authenticated_app):
    """Create a test client with authentication bypassed."""
    return TestClient(authenticated_app)


class TestPipelineRoutes:
    """Integration tests for pipeline routes."""
    
    def test_get_pipelines_list_returns_metadata(self, authenticated_client):
        """Test GET /pipelines/list returns pipeline metadata."""
        response = authenticated_client.get(
            "/pipelines/list",
            headers={"Authorization": "Bearer test_token"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "pipelines" in data
        pipelines = data["pipelines"]
        
        # Should have 3 pipelines
        assert len(pipelines) == 3
        
        # Check pipeline names
        names = [p["name"] for p in pipelines]
        assert "lex_intelligence" in names
        assert "calculus_intelligence" in names
        assert "forge_intelligence" in names
    
    def test_post_pipelines_run_with_valid_pipeline(self, authenticated_client):
        """Test POST /pipelines/run with valid pipeline (mocked execution)."""
        # Mock the pipeline execution
        mock_result = PipelineResult(
            pipeline_name="lex_intelligence",
            status="completed",
            output="Test output from mocked execution",
            agents_executed=["Agent 1", "Agent 2"],
            total_duration_ms=1500.0,
            metadata={"test": "data"},
        )
        
        with patch("backend.pipelines.registry.pipeline_registry.get_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.execute = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_pipeline
            
            response = authenticated_client.post(
                "/pipelines/run",
                json={
                    "pipeline_name": "lex_intelligence",
                    "input_data": {"query": "test query"},
                },
                headers={"Authorization": "Bearer test_token"},
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["pipeline_name"] == "lex_intelligence"
        assert data["status"] == "completed"
        assert data["output"] == "Test output from mocked execution"
        assert data["agents_executed"] == ["Agent 1", "Agent 2"]
        assert data["total_duration_ms"] == 1500.0
    
    def test_post_pipelines_run_with_unknown_pipeline(self, authenticated_client):
        """Test POST /pipelines/run with unknown pipeline returns error."""
        response = authenticated_client.post(
            "/pipelines/run",
            json={
                "pipeline_name": "nonexistent_pipeline",
                "input_data": {"query": "test"},
            },
            headers={"Authorization": "Bearer test_token"},
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_post_pipelines_run_without_auth_returns_401(self, app):
        """Test POST /pipelines/run without authentication returns 401."""
        # Use the non-authenticated client
        client = TestClient(app)
        
        response = client.post(
            "/pipelines/run",
            json={
                "pipeline_name": "lex_intelligence",
                "input_data": {"query": "test"},
            },
            # No Authorization header
        )
        
        assert response.status_code == 401
