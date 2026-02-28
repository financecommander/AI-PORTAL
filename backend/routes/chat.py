"""Chat routes — single-specialist conversations."""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import UsageLog
from backend.specialists.manager import get_specialist
from backend.providers.factory import get_provider

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=50000)


class ChatRequest(BaseModel):
    specialist_id: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=50000)
    conversation_history: list[ChatMessage] = Field(default_factory=list, max_length=100)


class ChatResponse(BaseModel):
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    specialist = get_specialist(request.specialist_id)
    provider = get_provider(specialist["provider"])

    messages = [m.model_dump() for m in request.conversation_history] + [{"role": "user", "content": request.message}]

    response = await provider.send_message(
        messages=messages,
        model=specialist["model"],
        temperature=specialist.get("temperature", 0.7),
        max_tokens=specialist.get("max_tokens", 4096),
        system_prompt=specialist.get("system_prompt"),
    )

    # Log usage
    log = UsageLog(
        user_hash=user.get("sub", "unknown"),
        provider=specialist["provider"],
        model=specialist["model"],
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
        latency_ms=response.latency_ms,
        specialist_id=request.specialist_id,
    )
    session.add(log)
    session.commit()

    return ChatResponse(
        content=response.content,
        model=response.model,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        latency_ms=response.latency_ms,
        cost_usd=response.cost_usd,
    )


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    specialist = get_specialist(request.specialist_id)
    provider = get_provider(specialist["provider"])

    messages = [m.model_dump() for m in request.conversation_history] + [{"role": "user", "content": request.message}]

    async def event_generator():
        final_chunk = None
        async for chunk in provider.stream_message(
            messages=messages,
            model=specialist["model"],
            temperature=specialist.get("temperature", 0.7),
            max_tokens=specialist.get("max_tokens", 4096),
            system_prompt=specialist.get("system_prompt"),
        ):
            if chunk.is_final:
                final_chunk = chunk
            data = {
                "content": chunk.content,
                "is_final": chunk.is_final,
                "input_tokens": chunk.input_tokens,
                "output_tokens": chunk.output_tokens,
                "cost_usd": chunk.cost_usd,
            }
            yield f"data: {json.dumps(data)}\n\n"

        # Log usage from the final chunk (mirrors /send behaviour)
        if final_chunk and final_chunk.input_tokens:
            log = UsageLog(
                user_hash=user.get("sub", "unknown"),
                provider=specialist["provider"],
                model=specialist["model"],
                input_tokens=final_chunk.input_tokens,
                output_tokens=final_chunk.output_tokens,
                cost_usd=final_chunk.cost_usd,
                latency_ms=0,
                specialist_id=request.specialist_id,
            )
            session.add(log)
            session.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
