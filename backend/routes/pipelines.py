"""Pipeline execution routes with WebSocket streaming."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from sqlmodel import Session
from backend.auth.authenticator import get_current_user
from backend.auth.jwt_handler import decode_access_token
from backend.database import get_session
from backend.models import PipelineRun
from backend.pipelines.registry import list_pipelines, get_pipeline
from backend.websockets.ws_manager import ws_manager


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
    """
    List all available pipelines.
    
    Returns:
        List of pipeline metadata
    """
    try:
        pipelines = list_pipelines()
        return {
            "pipelines": pipelines,
            "count": len(pipelines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipelines/run", response_model=PipelineExecuteResponse)
async def execute_pipeline(
    request: PipelineExecuteRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a pipeline and return results.
    Streams progress via WebSocket.
    
    Args:
        request: Pipeline execution request
        session: Database session
        current_user: Authenticated user
    
    Returns:
        Pipeline execution response with results
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
    
    # Define progress callback for WebSocket streaming
    async def on_progress(event_type: str, data: dict):
        """Broadcast progress updates via WebSocket."""
        await ws_manager.send_event(pipeline_id, event_type, data)
    
    # Execute pipeline
    try:
        result = await pipeline.execute(
            query=request.query,
            user_hash=user_hash,
            on_progress=on_progress
        )
        
        # Update database record (status: completed)
        pipeline_run.status = "completed"
        pipeline_run.output = result.output
        pipeline_run.total_tokens = result.total_tokens
        pipeline_run.total_cost = result.total_cost
        pipeline_run.duration_ms = result.duration_ms
        pipeline_run.agent_breakdown = json.dumps(result.agent_breakdown)
        pipeline_run.extra_metadata = json.dumps(result.metadata)
        pipeline_run.completed_at = datetime.now(timezone.utc)
        session.add(pipeline_run)
        session.commit()
        
        # Return response
        return PipelineExecuteResponse(
            pipeline_id=pipeline_id,
            status="completed",
            output=result.output,
            total_tokens=result.total_tokens,
            total_cost=result.total_cost,
            duration_ms=result.duration_ms,
            agent_breakdown=result.agent_breakdown,
            ws_url=f"/api/v2/pipelines/ws/{pipeline_id}"
        )
        
    except NotImplementedError as e:
        # Pipeline not yet implemented
        pipeline_run.status = "failed"
        pipeline_run.error = str(e)
        session.add(pipeline_run)
        session.commit()
        
        raise HTTPException(status_code=501, detail=str(e))
        
    except Exception as e:
        # Pipeline execution failed
        pipeline_run.status = "failed"
        pipeline_run.error = str(e)
        session.add(pipeline_run)
        session.commit()
        
        # Notify via WebSocket
        await ws_manager.send_event(pipeline_id, "error", {"message": str(e)})
        
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.websocket("/pipelines/ws/{pipeline_id}")
async def pipeline_websocket(
    websocket: WebSocket,
    pipeline_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time pipeline progress.
    
    Args:
        websocket: WebSocket connection
        pipeline_id: Pipeline execution ID
        token: Optional JWT token for authentication
    """
    # Optional authentication via query parameter
    if token:
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid authentication token")
            return
    
    # Connect to WebSocket manager
    await ws_manager.connect(pipeline_id, websocket)
    
    try:
        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            data = await websocket.receive_text()
            
            # Echo ping/pong for keep-alive
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        # Client disconnected
        await ws_manager.disconnect(pipeline_id, websocket)
    except Exception as e:
        # Unexpected error
        await ws_manager.disconnect(pipeline_id, websocket)
