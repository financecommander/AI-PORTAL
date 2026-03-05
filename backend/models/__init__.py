"""Database models for backend v2.3 — adds training data collection."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, ForeignKey
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
    extra_metadata: str = Field(default="{}")  # JSON string - renamed from metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


# ── v2.2: User accounts + conversation history ──────────────────


class User(SQLModel, table=True):
    """User accounts with OAuth or email login."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str = Field(default="")
    avatar_url: str = Field(default="")
    oauth_provider: str = Field(default="email")  # email, google, apple, x
    oauth_id: str = Field(default="")  # provider-specific user ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(SQLModel, table=True):
    """Persistent chat conversations."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)  # public-facing ID
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True),
    )
    title: str = Field(default="New conversation")
    provider: str = Field(default="")
    model: str = Field(default="")
    mode: str = Field(default="direct")  # direct, specialist
    specialist_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(SQLModel, table=True):
    """Individual messages within a conversation."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        sa_column=Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), index=True),
    )
    role: str  # user, assistant
    content: str
    model: str = Field(default="")
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── v2.3: Training data collection for swarm fine-tuning ─────


class TrainingData(SQLModel, table=True):
    """Training data captured from pipeline agent runs for fine-tuning."""

    __tablename__ = "training_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    pipeline_run_id: Optional[str] = Field(default=None, index=True)
    pipeline_name: str = Field(index=True)
    agent_name: str = Field(index=True)
    agent_role: str = Field(default="")
    model_used: str = Field(default="")
    system_prompt: str = Field(default="")
    user_input: str = Field(default="")
    assistant_output: str = Field(default="")
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    quality_score: Optional[float] = Field(default=None)  # 0.0-1.0, set by feedback
    quality_label: Optional[str] = Field(default=None)  # good, bad, needs_edit
    feedback_text: Optional[str] = Field(default=None)
    exported: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── v2.4: Conversation turns for knowledge distillation ──────


class ConversationTurn(SQLModel, table=True):
    """Logged conversation turn for knowledge distillation training data."""

    __tablename__ = "conversation_turns"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_hash: str = Field(index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(index=True)  # "specialist", "direct", "pipeline"
    provider: str
    model: str
    specialist_id: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: str
    assistant_response: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    exported: bool = Field(default=False, index=True)
