"""Test specialist routes."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@patch("backend.routes.specialists.load_specialists")
def test_list_specialists(mock_load, client: TestClient, auth_headers: dict):
    """Test GET /specialists/."""
    mock_load.return_value = [{"id": "test", "name": "Test Specialist"}]
    response = client.get("/specialists/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "specialists" in data


@patch("backend.routes.specialists.get_specialist")
def test_get_specialist(mock_get, client: TestClient, auth_headers: dict):
    """Test GET /specialists/{id}."""
    mock_get.return_value = {"id": "test", "name": "Test"}
    response = client.get("/specialists/test", headers=auth_headers)
    assert response.status_code == 200


@patch("backend.routes.specialists.get_specialist")
def test_get_specialist_invalid(mock_get, client: TestClient, auth_headers: dict):
    """Test GET /specialists/{invalid}."""
    mock_get.side_effect = ValueError("Not found")
    response = client.get("/specialists/invalid", headers=auth_headers)
    assert response.status_code == 500  # Assuming raises error


@patch("backend.routes.specialists.create_specialist")
def test_create_specialist(mock_create, client: TestClient, auth_headers: dict):
    """Test POST /specialists/ with valid data."""
    mock_create.return_value = {"id": "new", "name": "New Specialist"}
    response = client.post("/specialists/", json={"name": "New"}, headers=auth_headers)
    assert response.status_code == 200


def test_create_specialist_missing_fields(client: TestClient, auth_headers: dict):
    """Test POST /specialists/ with missing fields."""
    response = client.post("/specialists/", json={}, headers=auth_headers)
    assert response.status_code == 422


@patch("backend.routes.specialists.update_specialist")
def test_update_specialist(mock_update, client: TestClient, auth_headers: dict):
    """Test PUT /specialists/{id}."""
    mock_update.return_value = {"id": "test", "name": "Updated"}
    response = client.put("/specialists/test", json={"name": "Updated"}, headers=auth_headers)
    assert response.status_code == 200


@patch("backend.routes.specialists.delete_specialist")
def test_delete_specialist(mock_delete, client: TestClient, auth_headers: dict):
    """Test DELETE /specialists/{id}."""
    response = client.delete("/specialists/test", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"deleted": True}


def test_specialists_no_auth(client: TestClient):
    """Test all routes require auth."""
    routes = [
        ("GET", "/specialists/"),
        ("GET", "/specialists/test"),
        ("POST", "/specialists/"),
        ("PUT", "/specialists/test"),
        ("DELETE", "/specialists/test"),
    ]
    for method, path in routes:
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            response = client.post(path, json={})
        elif method == "PUT":
            response = client.put(path, json={})
        elif method == "DELETE":
            response = client.delete(path)
        assert response.status_code == 401