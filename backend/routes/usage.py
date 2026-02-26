"""Usage query routes."""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import UsageLog, PipelineRun

router = APIRouter()


@router.get("/logs")
async def get_usage_logs(
    limit: int = 50,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_hash = user.get("sub", "")
    stmt = select(UsageLog).where(UsageLog.user_hash == user_hash).order_by(UsageLog.timestamp.desc()).limit(limit)
    results = session.exec(stmt).all()
    return {"logs": [r.dict() for r in results]}


@router.get("/pipelines")
async def get_pipeline_runs(
    limit: int = 20,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_hash = user.get("sub", "")
    stmt = select(PipelineRun).where(PipelineRun.user_hash == user_hash).order_by(PipelineRun.created_at.desc()).limit(limit)
    results = session.exec(stmt).all()
    return {"runs": [r.dict() for r in results]}
