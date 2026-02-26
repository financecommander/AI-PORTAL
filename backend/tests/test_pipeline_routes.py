"""Test pipeline routes."""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


@patch("backend.routes.pipelines.list_pipelines")
def test_get_pipelines_list(mock_list, client: TestClient, auth_headers: dict):
    """Test GET /api/v2/pipelines/list."""
    mock_list.return_value = [{"name": "test-pipeline", "description": "Test"}]
    response = client.get("/api/v2/pipelines/list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "pipelines" in data
    assert "count" in data


@patch("backend.routes.pipelines.get_pipeline")
def test_execute_pipeline_valid(mock_get_pipeline, client: TestClient, auth_headers: dict):
    """Test POST /api/v2/pipelines/run with valid query."""
    mock_pipeline = AsyncMock()
    mock_pipeline.execute.return_value = AsyncMock(
        output="Test output",
        total_tokens=100,
        total_cost=0.01,
        duration_ms=500.0,
        agent_breakdown=[],
        metadata={}
    )
    mock_get_pipeline.return_value = mock_pipeline

    response = client.post("/api/v2/pipelines/run", json={
        "pipeline_name": "test-pipeline",
        "query": "Test query"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "pipeline_id" in data
    assert data["status"] == "completed"


def test_execute_pipeline_no_auth(client: TestClient):
    """Test POST /api/v2/pipelines/run without auth."""
    response = client.post("/api/v2/pipelines/run", json={
        "pipeline_name": "test",
        "query": "test"
    })
    assert response.status_code == 401


def test_execute_pipeline_empty_query(client: TestClient, auth_headers: dict):
    """Test POST /api/v2/pipelines/run with empty query."""
    response = client.post("/api/v2/pipelines/run", json={
        "pipeline_name": "test",
        "query": ""
    }, headers=auth_headers)
    assert response.status_code == 422  # Assuming validation


# Note: Mock CrewAI execution assumed