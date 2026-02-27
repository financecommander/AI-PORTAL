"""Pipeline execution routes with WebSocket streaming."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from sqlmodel import Session, select
from backend.auth.authenticator import get_current_user
from backend.auth.jwt_handler import decode_access_token
from backend.database import get_session, engine
from backend.models import PipelineRun
from backend.pipelines.registry import list_pipelines, get_pipeline
from backend.websockets.ws_manager import ws_manager

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class PipelineExecuteRequest(BaseModel):
    """Request model for pipeline execution."""
    pipeline_name: str
    query: str


class PipelineExecuteResponse(BaseModel):
    """Response model for pipeline execution."""
    pipeline_id: str
    status: str
    output: Optional[str] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    duration_ms: Optional[float] = None
    agent_breakdown: Optional[list[dict]] = None
    ws_url: str


@router.get("/pipelines/list")
async def get_pipelines_list(
    current_user: dict = Depends(get_current_user)
):
    """List all available pipelines."""
    try:
        pipelines = list_pipelines()
        return {
            "pipelines": pipelines,
            "count": len(pipelines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_pipeline_background(
    pipeline_name: str,
    pipeline_id: str,
    query: str,
    user_hash: str,
):
    """Execute pipeline in background and stream progress via WebSocket."""
    # Small delay to let WebSocket connect before first event
    await asyncio.sleep(0.5)

    try:
        pipeline = get_pipeline(pipeline_name)
    except KeyError as e:
        await ws_manager.send_event(pipeline_id, "error", {"message": str(e)})
        return

    async def on_progress(event_type: str, data: dict):
        """Broadcast progress updates via WebSocket."""
        await ws_manager.send_event(pipeline_id, event_type, data)

    try:
        result = await pipeline.execute(
            query=query,
            user_hash=user_hash,
            on_progress=on_progress
        )

        # Update database record
        with Session(engine) as session:
            statement = select(PipelineRun).where(PipelineRun.pipeline_id == pipeline_id)
            run = session.exec(statement).first()
            if run:
                run.status = "completed"
                run.output = result.output
                run.total_tokens = result.total_tokens
                run.total_cost = result.total_cost
                run.duration_ms = result.duration_ms
                run.agent_breakdown = json.dumps(result.agent_breakdown)
                run.extra_metadata = json.dumps(result.metadata)
                run.completed_at = datetime.now(timezone.utc)
                session.add(run)
                session.commit()

        # Send final complete event with full data
        await ws_manager.send_event(pipeline_id, "complete", {
            "output": result.output,
            "total_tokens": result.total_tokens,
            "total_cost": result.total_cost,
            "duration_ms": result.duration_ms,
            "agent_breakdown": result.agent_breakdown,
        })

    except Exception as e:
        logger.exception(f"Pipeline {pipeline_id} failed: {e}")
        # Update database record as failed
        with Session(engine) as session:
            statement = select(PipelineRun).where(PipelineRun.pipeline_id == pipeline_id)
            run = session.exec(statement).first()
            if run:
                run.status = "failed"
                session.add(run)
                session.commit()

        await ws_manager.send_event(pipeline_id, "error", {"message": str(e)})


@router.post("/pipelines/run", response_model=PipelineExecuteResponse)
async def execute_pipeline(
    request: PipelineExecuteRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Start a pipeline execution.
    Returns immediately with pipeline_id. Progress streams via WebSocket.
    """
    # Validate pipeline exists
    try:
        pipeline = get_pipeline(request.pipeline_name)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Generate pipeline ID
    pipeline_id = str(uuid.uuid4())
    user_hash = current_user.get("user_hash", "unknown")

    # Create database record (status: running)
    pipeline_run = PipelineRun(
        pipeline_id=pipeline_id,
        pipeline_name=request.pipeline_name,
        user_hash=user_hash,
        query=request.query,
        output="",
        total_tokens=0,
        total_cost=0.0,
        duration_ms=0.0,
        status="running",
        agent_breakdown="[]",
        extra_metadata="{}"
    )
    session.add(pipeline_run)
    session.commit()

    # Launch background execution — returns immediately
    asyncio.create_task(
        _run_pipeline_background(
            pipeline_name=request.pipeline_name,
            pipeline_id=pipeline_id,
            query=request.query,
            user_hash=user_hash,
        )
    )

    return PipelineExecuteResponse(
        pipeline_id=pipeline_id,
        status="running",
        ws_url=f"/api/v2/pipelines/ws/{pipeline_id}"
    )


@router.websocket("/pipelines/ws/{pipeline_id}")
async def pipeline_websocket(
    websocket: WebSocket,
    pipeline_id: str,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time pipeline progress."""
    if token:
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid authentication token")
            return

    await ws_manager.connect(pipeline_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(pipeline_id, websocket)
    except Exception:
        await ws_manager.disconnect(pipeline_id, websocket)
