import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

# Set env vars before importing anything
os.environ["DEBUG"] = "1"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ANTHROPIC_API_KEY"] = "test-key"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["XAI_API_KEY"] = "test-key"
os.environ["GOOGLE_API_KEY"] = "test-key"

# Mock all LLM provider API keys before importing app
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

@pytest.fixture
def client():
    """TestClient for FastAPI app."""
    from backend.main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Valid JWT auth headers for protected routes."""
    from backend.auth.jwt_handler import create_access_token
    token = create_access_token({"sub": "test@financecommander.com"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_provider():
    """Mock LLM provider that returns canned responses."""
    provider = AsyncMock()
    provider.chat.return_value = {
        "content": "Mock response",
        "tokens_used": {"prompt": 10, "completion": 20, "total": 30},
        "cost": 0.001,
        "model": "test-model"
    }
    provider.stream_chat = AsyncMock()
    return provider