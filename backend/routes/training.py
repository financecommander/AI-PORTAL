"""Training data API — browse, feedback, export, and synthetic generation."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select, func, col

from backend.auth.authenticator import get_current_user
from backend.database import engine
from backend.models import TrainingData
from backend.providers.fallback import get_provider_with_fallback

logger = logging.getLogger(__name__)
router = APIRouter()


class FeedbackRequest(BaseModel):
    quality_score: float = Field(..., ge=0.0, le=1.0)
    quality_label: str = Field(..., pattern=r"^(good|bad|needs_edit)$")
    feedback_text: Optional[str] = Field(default=None, max_length=2000)


@router.get("/data")
async def list_training_data(
    pipeline: Optional[str] = None,
    agent: Optional[str] = None,
    quality: Optional[str] = None,
    exported: Optional[bool] = None,
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    """Browse collected training data with optional filters."""
    with Session(engine) as session:
        stmt = select(TrainingData).order_by(col(TrainingData.created_at).desc())

        if pipeline:
            stmt = stmt.where(TrainingData.pipeline_name == pipeline)
        if agent:
            stmt = stmt.where(TrainingData.agent_name == agent)
        if quality:
            stmt = stmt.where(TrainingData.quality_label == quality)
        if exported is not None:
            stmt = stmt.where(TrainingData.exported == exported)

        stmt = stmt.offset(offset).limit(limit)
        rows = session.exec(stmt).all()

        return {
            "data": [
                {
                    "id": r.id,
                    "pipeline_name": r.pipeline_name,
                    "pipeline_run_id": r.pipeline_run_id,
                    "agent_name": r.agent_name,
                    "agent_role": r.agent_role,
                    "model_used": r.model_used,
                    "system_prompt": r.system_prompt[:200] + "..." if len(r.system_prompt) > 200 else r.system_prompt,
                    "user_input": r.user_input[:200] + "..." if len(r.user_input) > 200 else r.user_input,
                    "assistant_output": r.assistant_output[:300] + "..." if len(r.assistant_output) > 300 else r.assistant_output,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "cost_usd": r.cost_usd,
                    "quality_score": r.quality_score,
                    "quality_label": r.quality_label,
                    "feedback_text": r.feedback_text,
                    "exported": r.exported,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ],
            "offset": offset,
            "limit": limit,
        }


@router.get("/data/{data_id}")
async def get_training_data(data_id: int, user: dict = Depends(get_current_user)):
    """Get full training data entry (un-truncated)."""
    with Session(engine) as session:
        row = session.get(TrainingData, data_id)
        if not row:
            return JSONResponse(status_code=404, content={"error": "Not found"})
        return {
            "id": row.id,
            "pipeline_name": row.pipeline_name,
            "pipeline_run_id": row.pipeline_run_id,
            "agent_name": row.agent_name,
            "agent_role": row.agent_role,
            "model_used": row.model_used,
            "system_prompt": row.system_prompt,
            "user_input": row.user_input,
            "assistant_output": row.assistant_output,
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "cost_usd": row.cost_usd,
            "quality_score": row.quality_score,
            "quality_label": row.quality_label,
            "feedback_text": row.feedback_text,
            "exported": row.exported,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }


@router.post("/data/{data_id}/feedback")
async def submit_feedback(
    data_id: int, req: FeedbackRequest, user: dict = Depends(get_current_user)
):
    """Submit quality feedback for a training data entry."""
    with Session(engine) as session:
        row = session.get(TrainingData, data_id)
        if not row:
            return JSONResponse(status_code=404, content={"error": "Not found"})

        row.quality_score = req.quality_score
        row.quality_label = req.quality_label
        row.feedback_text = req.feedback_text
        session.add(row)
        session.commit()
        return {"status": "ok", "id": data_id}


@router.get("/export")
async def export_training_data(
    pipeline: Optional[str] = None,
    quality: Optional[str] = None,
    format: str = Query(default="chatml", pattern=r"^(chatml|alpaca)$"),
    user: dict = Depends(get_current_user),
):
    """Export training data as JSONL for fine-tuning."""
    with Session(engine) as session:
        stmt = select(TrainingData).order_by(col(TrainingData.created_at).asc())

        if pipeline:
            stmt = stmt.where(TrainingData.pipeline_name == pipeline)
        if quality:
            stmt = stmt.where(TrainingData.quality_label == quality)

        rows = session.exec(stmt).all()

        def generate_jsonl():
            for r in rows:
                if format == "chatml":
                    entry = {
                        "messages": [
                            {"role": "system", "content": r.system_prompt},
                            {"role": "user", "content": r.user_input},
                            {"role": "assistant", "content": r.assistant_output},
                        ]
                    }
                else:  # alpaca
                    entry = {
                        "instruction": r.system_prompt,
                        "input": r.user_input,
                        "output": r.assistant_output,
                    }

                # Add metadata
                entry["_meta"] = {
                    "pipeline": r.pipeline_name,
                    "agent": r.agent_name,
                    "model": r.model_used,
                    "quality": r.quality_label,
                }
                yield json.dumps(entry) + "\n"

            # Mark exported
            for r in rows:
                r.exported = True
                session.add(r)
            session.commit()

        filename = f"training_{pipeline or 'all'}.jsonl"
        return StreamingResponse(
            generate_jsonl(),
            media_type="application/x-ndjson",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )


@router.get("/stats")
async def training_stats(user: dict = Depends(get_current_user)):
    """Training data statistics."""
    with Session(engine) as session:
        total = session.exec(select(func.count(TrainingData.id))).one()

        # Per-pipeline counts
        pipeline_stmt = (
            select(TrainingData.pipeline_name, func.count(TrainingData.id))
            .group_by(TrainingData.pipeline_name)
        )
        pipelines = {name: count for name, count in session.exec(pipeline_stmt).all()}

        # Quality distribution
        quality_stmt = (
            select(TrainingData.quality_label, func.count(TrainingData.id))
            .where(TrainingData.quality_label.is_not(None))  # type: ignore
            .group_by(TrainingData.quality_label)
        )
        quality = {label: count for label, count in session.exec(quality_stmt).all()}

        # Export status
        exported_count = session.exec(
            select(func.count(TrainingData.id)).where(TrainingData.exported == True)
        ).one()

        return {
            "total": total,
            "by_pipeline": pipelines,
            "by_quality": quality,
            "exported": exported_count,
            "unexported": total - exported_count,
        }


# ── Synthetic Training Data Generation ────────────────────────


class GenerateRequest(BaseModel):
    pipeline_name: str = Field(..., min_length=1, max_length=100)
    count: int = Field(default=10, ge=1, le=100)
    base_on_existing: bool = Field(default=True)


@router.post("/generate")
async def generate_synthetic_data(
    req: GenerateRequest,
    user: dict = Depends(get_current_user),
):
    """Generate synthetic training data using Ollama (free, local inference).

    If ``base_on_existing`` is True, fetches high-quality existing rows for
    the requested pipeline and asks Ollama to generate variations. Otherwise,
    generates from scratch using the pipeline's domain knowledge.
    """
    provider, model = await get_provider_with_fallback(
        primary_model="deepseek-r1:14b",
        fallback_model="gemini-2.5-flash",
    )

    seed_rows: list[dict] = []
    if req.base_on_existing:
        with Session(engine) as session:
            stmt = (
                select(TrainingData)
                .where(TrainingData.pipeline_name == req.pipeline_name)
                .where(
                    (TrainingData.quality_label == "good")
                    | (TrainingData.quality_label.is_(None))  # type: ignore
                )
                .order_by(col(TrainingData.created_at).desc())
                .limit(10)
            )
            rows = session.exec(stmt).all()
            seed_rows = [
                {
                    "system_prompt": r.system_prompt[:2000],
                    "user_input": r.user_input[:2000],
                    "assistant_output": r.assistant_output[:3000],
                    "agent_name": r.agent_name,
                }
                for r in rows
            ]

    generated = 0
    errors = 0

    for i in range(req.count):
        try:
            if seed_rows:
                # Pick a seed row (round-robin)
                seed = seed_rows[i % len(seed_rows)]
                prompt = (
                    "Generate a DIFFERENT but structurally similar training example "
                    "for the same task. The output must be realistic and high-quality.\n\n"
                    f"Original system prompt:\n{seed['system_prompt']}\n\n"
                    f"Original user input:\n{seed['user_input']}\n\n"
                    f"Original assistant output (first 500 chars):\n{seed['assistant_output'][:500]}\n\n"
                    "Now generate a new, different example. Return ONLY valid JSON with:\n"
                    '{"user_input": "...", "assistant_output": "..."}\n\n'
                    "The system_prompt stays the same. Make the user_input a different scenario "
                    "and the assistant_output a high-quality response to that scenario."
                )
                agent_name = seed["agent_name"]
                system_prompt_text = seed["system_prompt"]
            else:
                prompt = (
                    f"Generate a realistic training example for the '{req.pipeline_name}' pipeline. "
                    "Return ONLY valid JSON with:\n"
                    '{"system_prompt": "...", "user_input": "...", "assistant_output": "..."}\n\n'
                    "Make it realistic, domain-specific, and high-quality."
                )
                agent_name = "synthetic"
                system_prompt_text = ""

            response = await provider.send_message(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.8,  # Higher temp for diversity
                max_tokens=2000,
                system_prompt="You are a training data generator. Return only valid JSON.",
            )

            # Parse JSON from response
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

            data = json.loads(text)

            # Save synthetic row
            with Session(engine) as session:
                row = TrainingData(
                    pipeline_name=req.pipeline_name,
                    agent_name=agent_name,
                    model_used=model if "/" in model else f"ollama/{model}",
                    system_prompt=data.get("system_prompt", system_prompt_text)[:4000],
                    user_input=data.get("user_input", "")[:4000],
                    assistant_output=data.get("assistant_output", "")[:8000],
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    cost_usd=0.0,
                    quality_label="synthetic",
                )
                session.add(row)
                session.commit()
                generated += 1

        except Exception as e:
            logger.warning("Synthetic generation %d/%d failed: %s", i + 1, req.count, e)
            errors += 1

    return {
        "generated": generated,
        "errors": errors,
        "pipeline": req.pipeline_name,
        "model_used": model,
    }
