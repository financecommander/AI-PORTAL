"""Chat endpoints for FastAPI backend."""

import hashlib
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sse_starlette.sse import EventSourceResponse

from backend.config.settings import settings
from backend.database.session import get_session
from backend.models.chat import ChatRequest, ChatResponse, StreamChunkResponse
from backend.models.usage_log import UsageLog
from config.pricing import estimate_cost
from providers import get_provider
from providers.base import ProviderResponse, StreamChunk
from specialists.manager import SpecialistManager

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize specialist manager
specialist_manager = SpecialistManager()


def _hash_email(email: str) -> str:
    """Hash email for privacy."""
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


async def _log_usage(
    session: Session,
    user_email: str,
    specialist_id: str,
    specialist_name: str,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: float,
    success: bool
) -> None:
    """Log usage to database."""
    cost = estimate_cost(model, input_tokens, output_tokens)
    
    usage_log = UsageLog(
        user_email_hash=_hash_email(user_email),
        specialist_id=specialist_id,
        specialist_name=specialist_name,
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=cost,
        latency_ms=latency_ms,
        success=success
    )
    
    session.add(usage_log)
    session.commit()


@router.post("/send", response_model=ChatResponse)
async def send_chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    user_email: str = "anonymous@example.com"  # TODO: Extract from auth
) -> ChatResponse:
    """
    Non-streaming chat endpoint.
    
    Flow:
    1. Validate specialist_id
    2. Retrieve provider via factory
    3. Compose messages (history + user query)
    4. Execute via provider.send_message()
    5. Log to database
    6. Return ChatResponse
    """
    start_time = time.perf_counter()
    
    # 1. Validate specialist
    specialist = specialist_manager.get(request.specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    
    # 2. Get provider
    try:
        provider = get_provider(specialist.provider, specialist.base_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 3. Compose messages
    messages = []
    for msg in request.conversation_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})
    
    # 4. Execute
    try:
        response: ProviderResponse = await provider.send_message(
            messages=messages,
            model=specialist.model,
            system_prompt=specialist.system_prompt,
            temperature=specialist.temperature,
            max_tokens=specialist.max_tokens
        )
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # 5. Log usage
        await _log_usage(
            session=session,
            user_email=user_email,
            specialist_id=specialist.id,
            specialist_name=specialist.name,
            provider=specialist.provider,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=latency_ms,
            success=True
        )
        
        # 6. Return response
        return ChatResponse(
            content=response.content,
            specialist_id=specialist.id,
            specialist_name=specialist.name,
            provider=specialist.provider,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            estimated_cost_usd=estimate_cost(
                response.model,
                response.input_tokens,
                response.output_tokens
            ),
            latency_ms=latency_ms
        )
        
    except Exception as e:
        # Log failure
        latency_ms = (time.perf_counter() - start_time) * 1000
        await _log_usage(
            session=session,
            user_email=user_email,
            specialist_id=specialist.id,
            specialist_name=specialist.name,
            provider=specialist.provider,
            model=specialist.model,
            input_tokens=0,
            output_tokens=0,
            latency_ms=latency_ms,
            success=False
        )
        raise HTTPException(status_code=500, detail=f"Provider error: {str(e)}")


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    user_email: str = "anonymous@example.com"  # TODO: Extract from auth
) -> EventSourceResponse:
    """
    Streaming chat endpoint with Server-Sent Events (SSE).
    
    Yields StreamChunk updates dynamically with data: formatting.
    Final chunk contains token counts and latency.
    """
    # Validate specialist
    specialist = specialist_manager.get(request.specialist_id)
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    
    # Get provider
    try:
        provider = get_provider(specialist.provider, specialist.base_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Compose messages
    messages = []
    for msg in request.conversation_history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})
    
    async def event_generator() -> AsyncGenerator[dict, None]:
        """Generate SSE events."""
        start_time = time.perf_counter()
        success = False
        final_chunk: StreamChunk | None = None
        
        try:
            async for chunk in provider.stream_message(
                messages=messages,
                model=specialist.model,
                system_prompt=specialist.system_prompt,
                temperature=specialist.temperature,
                max_tokens=specialist.max_tokens
            ):
                # Yield chunk as SSE event
                yield {
                    "event": "message",
                    "data": StreamChunkResponse(
                        content=chunk.content,
                        is_final=chunk.is_final,
                        input_tokens=chunk.input_tokens,
                        output_tokens=chunk.output_tokens,
                        model=chunk.model,
                        latency_ms=chunk.latency_ms
                    ).model_dump_json()
                }
                
                if chunk.is_final:
                    final_chunk = chunk
                    success = True
            
            # Log usage after stream completes
            if final_chunk:
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                # Note: Can't use async session in event generator easily
                # For now, we'll skip database logging in streaming mode
                # or implement a background task queue
                
        except Exception as e:
            # Send error event
            yield {
                "event": "error",
                "data": str(e)
            }
    
    return EventSourceResponse(event_generator())
