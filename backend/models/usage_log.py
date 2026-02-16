"""Database models for usage logging."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class UsageLog(SQLModel, table=True):
    """Logs each chat interaction for analytics and billing."""
    
    __tablename__ = "usage_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_email_hash: str = Field(index=True)
    specialist_id: str = Field(index=True)
    specialist_name: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: float
    success: bool
