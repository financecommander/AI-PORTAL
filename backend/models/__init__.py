"""
Database models for FinanceCommander AI Portal v2.0.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class UsageLog(SQLModel, table=True):
    """Tracks per-request usage and provider metrics."""
    
    __tablename__ = "usage_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_email_hash: str = Field(index=True)
    specialist_id: Optional[str] = Field(default=None, index=True)
    specialist_name: Optional[str] = Field(default=None)
    provider: str = Field(index=True)
    model: str = Field(index=True)
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    estimated_cost_usd: float = Field(default=0.0)
    latency_ms: float = Field(default=0.0)
    success: bool = Field(default=True)


class PipelineRun(SQLModel, table=True):
    """Tracks high-level pipeline execution metadata."""
    
    __tablename__ = "pipeline_runs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_email_hash: str = Field(index=True)
    pipeline_name: str = Field(index=True)
    status: str = Field(default="running")  # running, completed, failed
    total_tokens: int = Field(default=0)
    total_cost_usd: float = Field(default=0.0)
    duration_ms: int = Field(default=0)
    error_message: Optional[str] = Field(default=None)
    metadata_json: Optional[str] = Field(default=None)  # JSON string for additional data
