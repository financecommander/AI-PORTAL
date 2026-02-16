"""Test fixtures for backend tests."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database.session import get_session
from backend.main import app


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database session for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_specialist_manager(monkeypatch):
    """Mock specialist manager for tests."""
    from specialists.manager import Specialist
    
    test_specialist = Specialist(
        id="test-specialist-id",
        name="Test Specialist",
        provider="openai",
        model="gpt-4o",
        system_prompt="You are a test assistant.",
        temperature=0.7,
        max_tokens=1000
    )
    
    class MockSpecialistManager:
        def get(self, specialist_id: str):
            if specialist_id == "test-specialist-id":
                return test_specialist
            return None
    
    # Patch the specialist_manager in chat routes
    import backend.routes.chat as chat_module
    monkeypatch.setattr(chat_module, "specialist_manager", MockSpecialistManager())
    
    return test_specialist
