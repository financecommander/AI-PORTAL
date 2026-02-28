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


# ── Model Catalog (February 2026) ───────────────────────────────

PROVIDERS_CATALOG = [
    {
        "id": "openai",
        "name": "OpenAI",
        "models": [
            {
                "id": "gpt-5.2",
                "name": "GPT-5.2",
                "tier": "top",
                "context": "400K",
                "description": "Flagship model. Best for coding, agentic tasks, and reasoning.",
                "input_price": 1.75,
                "output_price": 14.00,
            },
            {
                "id": "gpt-5",
                "name": "GPT-5",
                "tier": "top",
                "context": "400K",
                "description": "Previous flagship. Unified thinking with smart routing.",
                "input_price": 1.25,
                "output_price": 10.00,
            },
            {
                "id": "gpt-4.1",
                "name": "GPT-4.1",
                "tier": "mid",
                "context": "1M",
                "description": "Smartest non-reasoning model. 1M context for long docs.",
                "input_price": 2.00,
                "output_price": 8.00,
            },
            {
                "id": "gpt-4.1-mini",
                "name": "GPT-4.1 Mini",
                "tier": "mid",
                "context": "1M",
                "description": "Best mid-range value. Excellent for bulk workloads.",
                "input_price": 0.40,
                "output_price": 1.60,
            },
            {
                "id": "gpt-4.1-nano",
                "name": "GPT-4.1 Nano",
                "tier": "budget",
                "context": "1M",
                "description": "Cheapest OpenAI. Fast classification and extraction.",
                "input_price": 0.10,
                "output_price": 0.40,
            },
            {
                "id": "o3-mini",
                "name": "o3-mini",
                "tier": "mid",
                "context": "200K",
                "description": "Reasoning specialist. Chain-of-thought for math/logic.",
                "input_price": 1.10,
                "output_price": 4.40,
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "tier": "budget",
                "context": "128K",
                "description": "Legacy budget model. Still great for simple tasks.",
                "input_price": 0.15,
                "output_price": 0.60,
            },
        ],
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "models": [
            {
                "id": "claude-opus-4-6",
                "name": "Claude Opus 4.6",
                "tier": "top",
                "context": "200K",
                "description": "Most intelligent. Adaptive thinking, agent teams, 1M beta.",
                "input_price": 5.00,
                "output_price": 25.00,
            },
            {
                "id": "claude-sonnet-4-6",
                "name": "Claude Sonnet 4.6",
                "tier": "top",
                "context": "200K",
                "description": "Near-Opus intelligence. 70% preferred over Sonnet 4.5 in coding.",
                "input_price": 3.00,
                "output_price": 15.00,
            },
            {
                "id": "claude-opus-4-5",
                "name": "Claude Opus 4.5",
                "tier": "mid",
                "context": "200K",
                "description": "Previous flagship. Deep analysis and creative writing.",
                "input_price": 5.00,
                "output_price": 25.00,
            },
            {
                "id": "claude-sonnet-4-5-20250929",
                "name": "Claude Sonnet 4.5",
                "tier": "mid",
                "context": "200K",
                "description": "Best coding value. Great for agentic workflows.",
                "input_price": 3.00,
                "output_price": 15.00,
            },
            {
                "id": "claude-haiku-4-5-20251001",
                "name": "Claude Haiku 4.5",
                "tier": "budget",
                "context": "200K",
                "description": "Speed champion. Near-instant responses, low cost.",
                "input_price": 1.00,
                "output_price": 5.00,
            },
        ],
    },
    {
        "id": "google",
        "name": "Google",
        "models": [
            {
                "id": "gemini-3.1-pro-preview",
                "name": "Gemini 3.1 Pro",
                "tier": "top",
                "context": "1M",
                "description": "Newest flagship. 77% ARC-AGI-2, native video & audio.",
                "input_price": 1.25,
                "output_price": 10.00,
            },
            {
                "id": "gemini-3-flash-preview",
                "name": "Gemini 3 Flash",
                "tier": "top",
                "context": "1M",
                "description": "Frontier speed + intelligence. Agentic capabilities.",
                "input_price": 0.50,
                "output_price": 3.00,
            },
            {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "tier": "mid",
                "context": "1M",
                "description": "Best for coding and complex reasoning. Hybrid thinking.",
                "input_price": 1.25,
                "output_price": 10.00,
            },
            {
                "id": "gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "tier": "mid",
                "context": "1M",
                "description": "Hybrid reasoning at ultra-low cost. Thinking budgets.",
                "input_price": 0.15,
                "output_price": 0.60,
            },
            {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "tier": "budget",
                "context": "1M",
                "description": "Fast multimodal. Free tier available in Google AI Studio.",
                "input_price": 0.10,
                "output_price": 0.40,
            },
        ],
    },
    {
        "id": "grok",
        "name": "xAI (Grok)",
        "models": [
            {
                "id": "grok-4",
                "name": "Grok 4",
                "tier": "top",
                "context": "256K",
                "description": "xAI flagship. PhD-level reasoning, real-time X data.",
                "input_price": 3.00,
                "output_price": 15.00,
            },
            {
                "id": "grok-4-1-fast",
                "name": "Grok 4.1 Fast",
                "tier": "mid",
                "context": "2M",
                "description": "Speed king. 2M context, 40% fewer thinking tokens.",
                "input_price": 0.20,
                "output_price": 0.50,
            },
            {
                "id": "grok-3",
                "name": "Grok 3",
                "tier": "mid",
                "context": "131K",
                "description": "Previous flagship. Strong reasoning and real-time knowledge.",
                "input_price": 3.00,
                "output_price": 15.00,
            },
        ],
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "models": [
            {
                "id": "deepseek-reasoner",
                "name": "DeepSeek R1",
                "tier": "top",
                "context": "128K",
                "description": "Best open-source reasoning. 90% cheaper than GPT-4 class.",
                "input_price": 0.55,
                "output_price": 2.19,
            },
            {
                "id": "deepseek-chat",
                "name": "DeepSeek V3.2",
                "tier": "mid",
                "context": "128K",
                "description": "GPT-4 level general chat. Incredible price/performance.",
                "input_price": 0.27,
                "output_price": 0.41,
            },
        ],
    },
    {
        "id": "mistral",
        "name": "Mistral AI",
        "models": [
            {
                "id": "mistral-large-latest",
                "name": "Mistral Large 3",
                "tier": "top",
                "context": "131K",
                "description": "Frontier MoE model. Strong reasoning, multilingual.",
                "input_price": 0.50,
                "output_price": 1.50,
            },
            {
                "id": "mistral-medium-latest",
                "name": "Mistral Medium 3",
                "tier": "mid",
                "context": "131K",
                "description": "Efficient MoE. Great balance of cost and capability.",
                "input_price": 0.40,
                "output_price": 2.00,
            },
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
