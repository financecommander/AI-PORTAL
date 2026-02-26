"""Chat routes — single-specialist conversations."""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import UsageLog
from backend.specialists.manager import get_specialist
from backend.providers.factory import get_provider

router = APIRouter()


class ChatRequest(BaseModel):
    specialist_id: str
    message: str
    conversation_history: list[dict] = []


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

    messages = request.conversation_history + [{"role": "user", "content": request.message}]

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
):
    specialist = get_specialist(request.specialist_id)
    provider = get_provider(specialist["provider"])

    messages = request.conversation_history + [{"role": "user", "content": request.message}]

    async def event_generator():
        async for chunk in provider.stream_message(
            messages=messages,
            model=specialist["model"],
            temperature=specialist.get("temperature", 0.7),
            max_tokens=specialist.get("max_tokens", 4096),
            system_prompt=specialist.get("system_prompt"),
        ):
            data = {
                "content": chunk.content,
                "is_final": chunk.is_final,
                "input_tokens": chunk.input_tokens,
                "output_tokens": chunk.output_tokens,
                "cost_usd": chunk.cost_usd,
            }
            yield f"data: {json.dumps(data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
