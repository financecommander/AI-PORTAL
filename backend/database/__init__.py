"""Database initialization and connection management."""

from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from backend.config.settings import settings


# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session (dependency for FastAPI routes)."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """Get a database session as a context manager (for non-DI usage)."""
    with Session(engine) as session:
        yield session
