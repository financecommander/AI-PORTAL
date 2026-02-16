"""API routes for pipeline execution and management."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.pipelines.base import AgentProgress
from backend.pipelines.registry import pipeline_registry
from backend.websockets.manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


# Request/Response models
class PipelineRunRequest(BaseModel):
    """Request to run a pipeline."""
    
    pipeline_name: str
    input_data: dict[str, Any]


class PipelineRunResponse(BaseModel):
    """Response from pipeline execution."""
    
    pipeline_name: str
    status: str
    output: str
    agents_executed: list[str]
    total_duration_ms: float
    error: str | None = None


# Mock authentication dependency
async def verify_token(authorization: str | None = None) -> dict:
    """Mock token verification.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        User info dict
        
    Raises:
        HTTPException: If no token provided
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")
    return {"user": "authenticated"}


@router.get("/list")
async def list_pipelines(user: dict = Depends(verify_token)):
    """List all available pipelines.
    
    Args:
        user: Authenticated user info
        
    Returns:
        List of pipeline metadata
    """
    pipelines = pipeline_registry.list_pipelines()
    return {"pipelines": pipelines}


@router.post("/run")
async def run_pipeline(
    request: PipelineRunRequest,
    user: dict = Depends(verify_token),
) -> PipelineRunResponse:
    """Execute a pipeline with the given input.
    
    Args:
        request: Pipeline run request
        user: Authenticated user info
        
    Returns:
        Pipeline execution result
        
    Raises:
        HTTPException: If pipeline not found or execution fails
    """
    try:
        # Get the pipeline
        pipeline = pipeline_registry.get_pipeline(request.pipeline_name)
        
        # Execute the pipeline
        result = await pipeline.execute(
            input_data=request.input_data,
            progress_callback=None,  # No WebSocket for direct calls
        )
        
        return PipelineRunResponse(
            pipeline_name=result.pipeline_name,
            status=result.status,
            output=result.output,
            agents_executed=result.agents_executed,
            total_duration_ms=result.total_duration_ms,
            error=result.error,
        )
        
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.websocket("/stream")
async def stream_pipeline(websocket: WebSocket):
    """WebSocket endpoint for streaming pipeline progress.
    
    Args:
        websocket: WebSocket connection
    """
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Wait for client message with pipeline request
            data = await websocket.receive_json()
            
            pipeline_name = data.get("pipeline_name")
            input_data = data.get("input_data", {})
            
            if not pipeline_name:
                await ws_manager.send_to(
                    websocket,
                    "error",
                    {"message": "Missing pipeline_name"},
                )
                continue
            
            try:
                # Get the pipeline
                pipeline = pipeline_registry.get_pipeline(pipeline_name)
                
                # Define progress callback
                async def send_progress(progress: AgentProgress):
                    await ws_manager.send_to(
                        websocket,
                        "progress",
                        {
                            "agent_name": progress.agent_name,
                            "status": progress.status.value,
                            "message": progress.message,
                            "timestamp": progress.timestamp.isoformat(),
                            "metadata": progress.metadata,
                        },
                    )
                
                # Execute the pipeline
                result = await pipeline.execute(
                    input_data=input_data,
                    progress_callback=send_progress,
                )
                
                # Send final result
                await ws_manager.send_to(
                    websocket,
                    "result",
                    {
                        "pipeline_name": result.pipeline_name,
                        "status": result.status,
                        "output": result.output,
                        "agents_executed": result.agents_executed,
                        "total_duration_ms": result.total_duration_ms,
                        "error": result.error,
                    },
                )
                
            except KeyError as e:
                await ws_manager.send_to(
                    websocket,
                    "error",
                    {"message": f"Pipeline not found: {str(e)}"},
                )
            except Exception as e:
                logger.error(f"WebSocket pipeline execution failed: {e}")
                await ws_manager.send_to(
                    websocket,
                    "error",
                    {"message": f"Pipeline execution failed: {str(e)}"},
                )
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
