"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data


class TestAuthEndpoints:
    """Tests for /auth endpoints."""
    
    def test_login_valid_email(self):
        """Test login with valid email."""
        response = client.post(
            "/auth/login",
            json={"email": "user@financecommander.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "user@financecommander.com"
    
    def test_login_invalid_domain(self):
        """Test login with invalid email domain."""
        response = client.post(
            "/auth/login",
            json={"email": "user@example.com"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_invalid_email_format(self):
        """Test login with invalid email format."""
        response = client.post(
            "/auth/login",
            json={"email": "invalid-email"}
        )
        
        assert response.status_code == 422  # Validation error


class TestChatEndpoints:
    """Tests for /chat endpoints (stubs)."""
    
    def test_send_message_stub(self):
        """Test chat endpoint returns stub response."""
        response = client.post("/chat/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"


class TestSpecialistEndpoints:
    """Tests for /specialists endpoints (stubs)."""
    
    def test_list_specialists_stub(self):
        """Test list specialists endpoint returns stub response."""
        response = client.get("/specialists/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"
    
    def test_create_specialist_stub(self):
        """Test create specialist endpoint returns stub response."""
        response = client.post("/specialists/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"


class TestPipelineEndpoints:
    """Tests for /pipelines endpoints (stubs)."""
    
    def test_list_pipelines_stub(self):
        """Test list pipelines endpoint returns stub response."""
        response = client.get("/pipelines/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"
    
    def test_run_pipeline_stub(self):
        """Test run pipeline endpoint returns stub response."""
        response = client.post("/pipelines/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"


class TestUsageEndpoints:
    """Tests for /usage endpoints (stubs)."""
    
    def test_get_usage_stub(self):
        """Test get usage endpoint returns stub response."""
        response = client.get("/usage/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"
