"""Direct LLM chat — provider/model selection without specialists."""

import json
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.auth.authenticator import get_current_user
from backend.config.settings import settings
from backend.database import get_session
from backend.models import UsageLog
from backend.providers.factory import get_provider
from sqlmodel import Session

logger = logging.getLogger(__name__)
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
    {
        "id": "groq",
        "name": "Groq (Llama)",
        "models": [
            {
                "id": "meta-llama/llama-4-maverick-17b-128e-instruct",
                "name": "Llama 4 Maverick",
                "tier": "top",
                "context": "128K",
                "description": "Meta's flagship MoE model via Groq — 562 tok/s, multimodal",
                "input_price": 0.20, "output_price": 0.60
            },
            {
                "id": "meta-llama/llama-4-scout-17b-16e-instruct",
                "name": "Llama 4 Scout",
                "tier": "mid",
                "context": "128K",
                "description": "Fast general-purpose MoE via Groq — 594 tok/s, reasoning & code",
                "input_price": 0.11, "output_price": 0.34
            },
        ]
    },
]

# Build a lookup set for validation: model_id -> provider_id
_VALID_MODELS: dict[str, str] = {}
for _prov in PROVIDERS_CATALOG:
    for _m in _prov["models"]:
        _VALID_MODELS[_m["id"]] = _prov["id"]

# Map provider_id -> settings attribute name for API key check
_PROVIDER_KEY_ATTRS: dict[str, str] = {
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
    "google": "google_api_key",
    "grok": "xai_api_key",
}


@router.get("/models")
async def list_models(user: dict = Depends(get_current_user)):
    """Return the model catalog, filtered to providers with configured API keys."""
    available = []
    for prov in PROVIDERS_CATALOG:
        key_attr = _PROVIDER_KEY_ATTRS.get(prov["id"])
        if key_attr and getattr(settings, key_attr, ""):
            available.append(prov)
    return {"providers": available}


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

    # Validate model exists in catalog
    if request.model not in _VALID_MODELS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unknown model '{request.model}'. Use GET /chat/direct/models for available models."},
        )

    # Validate provider/model pairing
    expected_provider = _VALID_MODELS[request.model]
    if request.provider != expected_provider:
        return JSONResponse(
            status_code=400,
            content={"error": f"Model '{request.model}' belongs to provider '{expected_provider}', not '{request.provider}'."},
        )

    # Check API key is configured
    key_attr = _PROVIDER_KEY_ATTRS.get(request.provider)
    if key_attr and not getattr(settings, key_attr, ""):
        return JSONResponse(
            status_code=400,
            content={"error": f"API key for {request.provider} is not configured. Contact your administrator."},
        )

    provider = get_provider(request.provider)
    messages = (
        [m.model_dump() for m in request.conversation_history]
        + [{"role": "user", "content": request.message}]
    )

    async def event_generator():
        final_chunk = None
        try:
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
        except Exception as e:
            logger.error("Direct chat stream error: %s", e)
            error_data = {"content": "", "is_final": True, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0, "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        # Log usage with actual latency
        if final_chunk and final_chunk.input_tokens:
            log = UsageLog(
                user_hash=user.get("sub", "unknown"),
                provider=request.provider,
                model=request.model,
                input_tokens=final_chunk.input_tokens,
                output_tokens=final_chunk.output_tokens,
                cost_usd=final_chunk.cost_usd,
                latency_ms=final_chunk.latency_ms,
                specialist_id="direct",
            )
            session.add(log)
            session.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
