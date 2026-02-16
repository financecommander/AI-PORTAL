"""Database models for backend v2.0."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class UsageLog(SQLModel, table=True):
    """Usage log for individual requests."""
    
    __tablename__ = "usage_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_hash: str = Field(index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    specialist_id: Optional[str] = None


class PipelineRun(SQLModel, table=True):
    """High-level pipeline execution log."""
    
    __tablename__ = "pipeline_runs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pipeline_id: str = Field(index=True, unique=True)
    pipeline_name: str
    user_hash: str = Field(index=True)
    query: str
    output: str
    total_tokens: int
    total_cost: float
    duration_ms: float
    status: str  # running, completed, failed
    error: Optional[str] = None
    agent_breakdown: str  # JSON string
    metadata: str  # JSON string
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
