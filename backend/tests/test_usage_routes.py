"""Test usage routes."""

import pytest
from fastapi.testclient import TestClient


def test_get_usage_logs_auth(client: TestClient, auth_headers: dict):
    """Test GET /usage/logs with auth."""
    response = client.get("/usage/logs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)


def test_get_usage_logs_no_auth(client: TestClient):
    """Test GET /usage/logs without auth."""
    response = client.get("/usage/logs")
    assert response.status_code == 401


# Note: Schema verification would require actual data, but assuming the model has the fields