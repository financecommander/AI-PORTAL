"""Request and response models for chat endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in the conversation."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    specialist_id: str = Field(..., description="ID of the specialist to use")
    message: str = Field(..., description="User message")
    conversation_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Optional conversation history"
    )


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    content: str = Field(..., description="Assistant's response")
    specialist_id: str
    specialist_name: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    latency_ms: float


class StreamChunkResponse(BaseModel):
    """Single chunk in streaming response."""
    content: str
    is_final: bool
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    latency_ms: float = 0.0
