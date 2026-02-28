"""Direct LLM chat — provider/model selection without specialists."""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import UsageLog
from backend.providers.factory import get_provider
from sqlmodel import Session

router = APIRouter()


# ── Model Catalog ────────────────────────────────────────────────

PROVIDERS_CATALOG = [
    {
        "id": "openai",
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o", "tier": "top", "input_price": 2.50, "output_price": 10.00},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "tier": "mid", "input_price": 0.15, "output_price": 0.60},
            {"id": "o3-mini", "name": "o3-mini", "tier": "top", "input_price": 1.10, "output_price": 4.40},
        ],
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "models": [
            {"id": "claude-sonnet-4", "name": "Claude Sonnet 4", "tier": "top", "input_price": 3.00, "output_price": 15.00},
            {"id": "claude-haiku-4", "name": "Claude Haiku 4", "tier": "mid", "input_price": 0.25, "output_price": 1.25},
        ],
    },
    {
        "id": "google",
        "name": "Google",
        "models": [
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "tier": "top", "input_price": 1.25, "output_price": 10.00},
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "tier": "mid", "input_price": 0.15, "output_price": 0.60},
        ],
    },
    {
        "id": "grok",
        "name": "Grok (xAI)",
        "models": [
            {"id": "grok-3", "name": "Grok 3", "tier": "top", "input_price": 5.00, "output_price": 15.00},
            {"id": "grok-3-mini", "name": "Grok 3 Mini", "tier": "mid", "input_price": 0.30, "output_price": 0.50},
        ],
    },
]

# Build a lookup set for validation
_VALID_MODELS: dict[str, str] = {}  # model_id -> provider_id
for _prov in PROVIDERS_CATALOG:
    for _m in _prov["models"]:
        _VALID_MODELS[_m["id"]] = _prov["id"]


@router.get("/models")
async def list_models(user: dict = Depends(get_current_user)):
    """Return the curated model catalog for the direct chat UI."""
    return {"providers": PROVIDERS_CATALOG}


# ── Streaming Chat ───────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=50000)


class DirectChatRequest(BaseModel):
    provider: str = Field(..., min_length=1, max_length=30)
    model: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=50000)
    conversation_history: list[ChatMessage] = Field(default_factory=list, max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=32768)


@router.post("/stream")
async def stream_direct_chat(
    request: DirectChatRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Stream a direct LLM response — no specialist, user picks provider + model."""

    # Validate provider/model combo
    if request.model not in _VALID_MODELS:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=400,
            content={"error": f"Unknown model '{request.model}'. Use GET /chat/direct/models for available models."},
        )

    provider = get_provider(request.provider)
    messages = (
        [m.model_dump() for m in request.conversation_history]
        + [{"role": "user", "content": request.message}]
    )

    async def event_generator():
        final_chunk = None
        async for chunk in provider.stream_message(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt="You are a helpful AI assistant.",
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

        # Log usage
        if final_chunk and final_chunk.input_tokens:
            log = UsageLog(
                user_hash=user.get("sub", "unknown"),
                provider=request.provider,
                model=request.model,
                input_tokens=final_chunk.input_tokens,
                output_tokens=final_chunk.output_tokens,
                cost_usd=final_chunk.cost_usd,
                latency_ms=0,
                specialist_id="direct",
            )
            session.add(log)
            session.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
