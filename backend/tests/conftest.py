"""
Test fixtures for backend v2.0 tests.
"""
import pytest
from sqlmodel import create_engine, Session, SQLModel
from backend.config.settings import Settings


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    return Settings(
        DATABASE_URL="sqlite:///./test.db",
        JWT_SECRET_KEY="test-secret-key",
        OPENAI_API_KEY="test-openai-key",
        ANTHROPIC_API_KEY="test-anthropic-key",
        GOOGLE_API_KEY="test-google-key",
        DEBUG=False,
    )


@pytest.fixture
def test_db(test_settings):
    """Create a test database."""
    engine = create_engine(test_settings.DATABASE_URL, echo=False)
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session(test_db):
    """Create a database session for testing."""
    with Session(test_db) as session:
        yield session


@pytest.fixture
def session(test_db):
    """Alias for db_session to support different naming conventions."""
    with Session(test_db) as session:
        yield session
