"""Distillation routes — training data stats, export, and readiness checks."""

import json
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import ConversationTurn
from backend.distillation.training import check_readiness, get_training_instructions

router = APIRouter()

RECOMMENDED_MIN_TURNS = 5000


@router.get("/stats")
async def distillation_stats(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return conversation turn counts and breakdowns."""
    total = session.exec(
        select(func.count(ConversationTurn.id))
    ).one()

    unexported = session.exec(
        select(func.count(ConversationTurn.id)).where(ConversationTurn.exported == False)
    ).one()

    # Group by provider
    by_provider_rows = session.exec(
        select(ConversationTurn.provider, func.count(ConversationTurn.id))
        .group_by(ConversationTurn.provider)
    ).all()
    by_provider = {row[0]: row[1] for row in by_provider_rows}

    # Group by source
    by_source_rows = session.exec(
        select(ConversationTurn.source, func.count(ConversationTurn.id))
        .group_by(ConversationTurn.source)
    ).all()
    by_source = {row[0]: row[1] for row in by_source_rows}

    return {
        "total_turns": total,
        "unexported_count": unexported,
        "by_provider": by_provider,
        "by_source": by_source,
    }


@router.get("/readiness")
async def distillation_readiness(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Check if enough data has been collected for fine-tuning."""
    total = session.exec(
        select(func.count(ConversationTurn.id))
    ).one()

    # Exportable = turns with at least some meaningful output
    exportable = session.exec(
        select(func.count(ConversationTurn.id)).where(
            ConversationTurn.output_tokens >= 50
        )
    ).one()

    return {
        "total_turns": total,
        "exportable": exportable,
        "recommended_min": RECOMMENDED_MIN_TURNS,
        "ready": exportable >= RECOMMENDED_MIN_TURNS,
    }


@router.get("/export")
async def export_training_data(
    format: str = Query(default="alpaca", pattern=r"^(alpaca)$"),
    min_output_tokens: int = Query(default=50, ge=0),
    limit: int = Query(default=5000, ge=1, le=50000),
    mark_exported: bool = Query(default=True),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Export conversation turns as Alpaca-format JSONL for fine-tuning.

    Each line: {"instruction": <system_prompt>, "input": <user_prompt>, "output": <assistant_response>}
    """
    stmt = (
        select(ConversationTurn)
        .where(ConversationTurn.output_tokens >= min_output_tokens)
        .order_by(ConversationTurn.timestamp)
        .limit(limit)
    )
    turns = session.exec(stmt).all()

    def generate_jsonl():
        ids_to_mark = []
        for turn in turns:
            record = {
                "instruction": turn.system_prompt or "You are a helpful AI assistant.",
                "input": turn.user_prompt,
                "output": turn.assistant_response,
            }
            yield json.dumps(record, ensure_ascii=False) + "\n"
            ids_to_mark.append(turn.id)

        # Mark as exported after streaming
        if mark_exported and ids_to_mark:
            for turn_id in ids_to_mark:
                turn_obj = session.get(ConversationTurn, turn_id)
                if turn_obj:
                    turn_obj.exported = True
            session.commit()

    return StreamingResponse(
        generate_jsonl(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "attachment; filename=training_data.jsonl"},
    )


@router.post("/train")
async def get_training_plan(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return training readiness check and step-by-step instructions."""
    readiness = check_readiness(session)
    return get_training_instructions(readiness)
