"""Chat routes — single-specialist conversations with file attachment support.

Includes:
- /send       — one-shot message to a specialist
- /stream     — streaming response from a specialist (with compliance pre-screen)
- /triage     — Ollama-powered specialist recommendation from user query
"""

import asyncio
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import UsageLog
from backend.specialists.manager import get_specialist, load_specialists
from backend.providers.factory import get_provider
from backend.providers.fallback import get_provider_with_fallback
from backend.utils.file_handler import process_attachments
from backend.utils.distillation_logger import log_conversation_turn

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / response models ──────────────────────────────────


class AttachmentPayload(BaseModel):
    """A single file attachment (base64-encoded, validated server-side)."""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=100)
    data_base64: str = Field(..., min_length=1)
    size_bytes: int = Field(..., gt=0, le=10 * 1024 * 1024)  # max 10 MB


class ChatMessage(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=50000)


class ChatRequest(BaseModel):
    specialist_id: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=50000)
    conversation_history: list[ChatMessage] = Field(default_factory=list, max_length=100)
    attachments: list[AttachmentPayload] = Field(default_factory=list, max_length=5)


class TriageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float


# ── Message builder ────────────────────────────────────────────


def build_messages_with_attachments(
    history: list[ChatMessage],
    message: str,
    attachments: list[AttachmentPayload],
    provider_name: str,
) -> list[dict]:
    """Build the messages list, converting the current user message into a
    multipart content array if attachments are present.

    History messages remain as simple {role, content: str} — only the
    current user message gets rich content blocks with images/docs.
    """
    messages = [m.model_dump() for m in history]

    if not attachments:
        messages.append({"role": "user", "content": message})
        return messages

    # Format attachments into provider-specific content blocks
    attachment_blocks = process_attachments(attachments, provider_name)

    # Build content array: text first, then attachment blocks
    content_parts: list[dict] = [{"type": "text", "text": message}]
    content_parts.extend(attachment_blocks)

    messages.append({"role": "user", "content": content_parts})
    return messages


# ── Endpoints ──────────────────────────────────────────────────


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    specialist = get_specialist(request.specialist_id)
    provider = get_provider(specialist["provider"])

    messages = build_messages_with_attachments(
        request.conversation_history,
        request.message,
        request.attachments,
        specialist["provider"],
    )

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
    try:
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()

    # Log conversation turn for distillation
    asyncio.create_task(log_conversation_turn(
        user_hash=user.get("sub", "unknown"),
        source="specialist",
        provider=specialist["provider"],
        model=specialist["model"],
        specialist_id=request.specialist_id,
        system_prompt=specialist.get("system_prompt", ""),
        user_prompt=request.message,
        assistant_response=response.content,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cost_usd=response.cost_usd,
    ))

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

    # ── Compliance Pre-Screen (Ollama fast-pass) ──────────────
    # For compliance-scanner requests with no prior history, try a quick
    # Ollama pre-screen first.  If the local model finds NO issues, stream
    # its response directly (free + fast).  If it flags POTENTIAL_ISSUES,
    # escalate to the full Gemini compliance scanner.
    use_prescreen = (
        request.specialist_id == "compliance-scanner"
        and len(request.conversation_history) == 0
        and not request.attachments
    )

    if use_prescreen:
        prescreen_result = await _compliance_prescreen(request.message)
        if prescreen_result is not None:
            # Ollama found no issues — stream its response directly
            async def prescreen_generator():
                data = {
                    "content": prescreen_result,
                    "is_final": True,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                }
                yield f"data: {json.dumps(data)}\n\n"

            logger.info("Compliance pre-screen: NO_ISSUES — returning Ollama fast-pass")
            return StreamingResponse(prescreen_generator(), media_type="text/event-stream")

    # ── Standard flow ─────────────────────────────────────────
    provider = get_provider(specialist["provider"])

    messages = build_messages_with_attachments(
        request.conversation_history,
        request.message,
        request.attachments,
        specialist["provider"],
    )

    # Auto-summarize if history exceeds ~70% of model context window
    try:
        from backend.utils.summarizer import summarize_history
        messages, _ = await summarize_history(messages, specialist["model"])
    except Exception as e:
        logger.warning("Summarization check failed (continuing with full history): %s", e)

    async def event_generator():
        final_chunk = None
        response_text = ""
        async for chunk in provider.stream_message(
            messages=messages,
            model=specialist["model"],
            temperature=specialist.get("temperature", 0.7),
            max_tokens=specialist.get("max_tokens", 4096),
            system_prompt=specialist.get("system_prompt"),
        ):
            if chunk.is_final:
                final_chunk = chunk
            if chunk.content:
                response_text += chunk.content
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
            try:
                session.add(log)
                session.commit()
            except Exception:
                session.rollback()

            # Log conversation turn for distillation
            asyncio.create_task(log_conversation_turn(
                user_hash=user.get("sub", "unknown"),
                source="specialist",
                provider=specialist["provider"],
                model=specialist["model"],
                specialist_id=request.specialist_id,
                system_prompt=specialist.get("system_prompt", ""),
                user_prompt=request.message,
                assistant_response=response_text,
                input_tokens=final_chunk.input_tokens,
                output_tokens=final_chunk.output_tokens,
                cost_usd=final_chunk.cost_usd,
            ))

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Compliance Pre-Screen ─────────────────────────────────────


async def _compliance_prescreen(message: str) -> Optional[str]:
    """Quick Ollama pre-screen for compliance queries.

    Returns the Ollama response if NO issues are found (fast-pass),
    or None if issues are flagged (escalate to full Gemini scanner).
    Returns None if Ollama is unreachable.
    """
    try:
        provider, model = await get_provider_with_fallback(
            primary_model="deepseek-r1:14b",
            fallback_model="__skip__",  # sentinel — skip pre-screen if Ollama down
        )
        if model == "__skip__":
            return None

        system_prompt = (
            "You are a fast compliance pre-screening agent. Analyze the query for potential "
            "regulatory compliance issues across SEC, FINRA, CFPB, state lending laws, and "
            "financial technology regulations.\n\n"
            "If you find NO compliance concerns, start your response with the exact tag "
            "[NO_ISSUES_FOUND] and then provide a brief explanation.\n\n"
            "If you find ANY potential compliance concerns, start your response with the exact "
            "tag [POTENTIAL_ISSUES] and list the concerns briefly.\n\n"
            "Be conservative — flag anything ambiguous as POTENTIAL_ISSUES."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": message}],
            model=model,
            temperature=0.1,
            max_tokens=1000,
            system_prompt=system_prompt,
        )

        content = response.content.strip()
        if content.startswith("[NO_ISSUES_FOUND]"):
            # Clean the tag and return the explanation
            clean = content.replace("[NO_ISSUES_FOUND]", "").strip()
            return (
                "**Compliance Pre-Screen** (Ollama fast-pass)\n\n"
                f"{clean}\n\n"
                "*No compliance issues detected. For a deeper analysis, send a follow-up message.*"
            )

        # Issues found or ambiguous — escalate to full scanner
        return None

    except Exception as e:
        logger.warning("Compliance pre-screen failed: %s — escalating to full scanner", e)
        return None


# ── Specialist Triage Router ──────────────────────────────────


@router.post("/triage")
async def triage_query(
    request: TriageRequest,
    user: dict = Depends(get_current_user),
):
    """Classify a user query and recommend the best specialist.

    Uses Ollama for free, fast classification. Falls back to a simple
    keyword-based ranking if Ollama is unavailable.
    """
    specialists = load_specialists()

    # Build the specialist catalog for the classifier
    catalog_lines = []
    for s in specialists:
        catalog_lines.append(f'- id="{s["id"]}" | {s["name"]}: {s["description"]}')
    catalog = "\n".join(catalog_lines)

    system_prompt = (
        "You are a specialist routing agent. Given a user query and a catalog of "
        "available AI specialists, recommend the top 3 best-matching specialists.\n\n"
        f"Available specialists:\n{catalog}\n\n"
        "Return ONLY a JSON array (no markdown) with exactly 3 objects:\n"
        '  [{"specialist_id": "...", "confidence": 0.0-1.0, "reason": "one sentence"}]\n\n'
        "Rank by relevance. The first item should be the best match."
    )

    try:
        provider, model = await get_provider_with_fallback(
            primary_model="deepseek-r1:14b",
            fallback_model="gemini-2.5-flash",
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": request.message}],
            model=model,
            temperature=0.1,
            max_tokens=500,
            system_prompt=system_prompt,
        )

        # Parse JSON from response
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        recommendations = json.loads(text)

        # Validate specialist IDs exist
        valid_ids = {s["id"] for s in specialists}
        recommendations = [
            r for r in recommendations
            if isinstance(r, dict) and r.get("specialist_id") in valid_ids
        ][:3]

        return {
            "recommendations": recommendations,
            "model_used": model,
        }

    except Exception as e:
        logger.warning("Triage classification failed: %s — returning default order", e)
        # Fallback: return first 3 specialists in default order
        return {
            "recommendations": [
                {"specialist_id": s["id"], "confidence": 0.5, "reason": "Default ordering"}
                for s in specialists[:3]
            ],
            "model_used": "fallback",
        }
