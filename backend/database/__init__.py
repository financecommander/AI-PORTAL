"""
Database initialization and logging functions.
"""
import hashlib
from datetime import datetime
from typing import Optional
from sqlmodel import Session, SQLModel, create_engine
from backend.config.settings import settings
from backend.models import UsageLog, PipelineRun


# Create engine
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def log_usage(
    user_email: str,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    estimated_cost_usd: float,
    latency_ms: float,
    success: bool = True,
    specialist_id: Optional[str] = None,
    specialist_name: Optional[str] = None,
):
    """Log usage metrics to database."""
    # Hash email for privacy
    email_hash = hashlib.sha256(user_email.encode()).hexdigest()
    
    usage_log = UsageLog(
        user_email_hash=email_hash,
        specialist_id=specialist_id,
        specialist_name=specialist_name,
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
        latency_ms=latency_ms,
        success=success,
    )
    
    with Session(engine) as session:
        session.add(usage_log)
        session.commit()
        session.refresh(usage_log)
        return usage_log


def log_pipeline_run(
    user_email: str,
    pipeline_name: str,
    status: str = "running",
    total_tokens: int = 0,
    total_cost_usd: float = 0.0,
    duration_ms: int = 0,
    error_message: Optional[str] = None,
    metadata_json: Optional[str] = None,
):
    """Log pipeline run metadata to database."""
    # Hash email for privacy
    email_hash = hashlib.sha256(user_email.encode()).hexdigest()
    
    pipeline_run = PipelineRun(
        user_email_hash=email_hash,
        pipeline_name=pipeline_name,
        status=status,
        total_tokens=total_tokens,
        total_cost_usd=total_cost_usd,
        duration_ms=duration_ms,
        error_message=error_message,
        metadata_json=metadata_json,
    )
    
    with Session(engine) as session:
        session.add(pipeline_run)
        session.commit()
        session.refresh(pipeline_run)
        return pipeline_run
