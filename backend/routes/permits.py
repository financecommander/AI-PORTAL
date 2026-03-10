"""Permit search API — browse, filter, and stats for ingested permits."""

import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func, col, or_

from backend.auth.authenticator import get_current_user
from backend.database import engine
from backend.models import Permit, PermitIngestionRun

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search")
async def search_permits(
    city: Optional[str] = None,
    permit_type: Optional[str] = None,
    lead_tier: Optional[str] = None,
    ai_tag: Optional[str] = None,
    property_type: Optional[str] = None,
    project_category: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    address: Optional[str] = None,
    applicant: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = Query(default="created_at", pattern=r"^(created_at|lead_score|estimated_cost|issue_date)$"),
    order: str = Query(default="desc", pattern=r"^(asc|desc)$"),
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    """Search and filter permits with full-text and faceted search."""
    with Session(engine) as session:
        stmt = select(Permit)

        if city:
            stmt = stmt.where(Permit.city.ilike(f"%{city}%"))  # type: ignore
        if permit_type:
            stmt = stmt.where(Permit.permit_type.ilike(f"%{permit_type}%"))  # type: ignore
        if lead_tier:
            stmt = stmt.where(Permit.lead_tier == lead_tier)
        if ai_tag:
            stmt = stmt.where(Permit.ai_tags.contains(ai_tag))  # type: ignore
        if property_type:
            stmt = stmt.where(Permit.ai_property_type == property_type)
        if project_category:
            stmt = stmt.where(Permit.ai_project_category == project_category)
        if min_cost is not None:
            stmt = stmt.where(Permit.estimated_cost >= min_cost)
        if max_cost is not None:
            stmt = stmt.where(Permit.estimated_cost <= max_cost)
        if address:
            stmt = stmt.where(Permit.address.ilike(f"%{address}%"))  # type: ignore
        if applicant:
            stmt = stmt.where(
                or_(
                    Permit.applicant_name.ilike(f"%{applicant}%"),  # type: ignore
                    Permit.contractor_name.ilike(f"%{applicant}%"),  # type: ignore
                    Permit.owner_name.ilike(f"%{applicant}%"),  # type: ignore
                )
            )
        if q:
            stmt = stmt.where(
                or_(
                    Permit.work_description.ilike(f"%{q}%"),  # type: ignore
                    Permit.address.ilike(f"%{q}%"),  # type: ignore
                    Permit.applicant_name.ilike(f"%{q}%"),  # type: ignore
                    Permit.permit_number.ilike(f"%{q}%"),  # type: ignore
                )
            )

        # Sorting
        sort_col = getattr(Permit, sort, Permit.created_at)
        if order == "desc":
            stmt = stmt.order_by(col(sort_col).desc())
        else:
            stmt = stmt.order_by(col(sort_col).asc())

        # Count total before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = session.exec(count_stmt).one()

        stmt = stmt.offset(offset).limit(limit)
        rows = session.exec(stmt).all()

        return {
            "data": [_permit_to_dict(r) for r in rows],
            "total": total,
            "offset": offset,
            "limit": limit,
        }


@router.get("/stats")
async def permit_stats(user: dict = Depends(get_current_user)):
    """Aggregate permit statistics."""
    with Session(engine) as session:
        total = session.exec(select(func.count(Permit.id))).one()

        # By city
        city_stmt = (
            select(Permit.city, func.count(Permit.id))
            .group_by(Permit.city)
        )
        by_city = {city: count for city, count in session.exec(city_stmt).all()}

        # By lead tier
        tier_stmt = (
            select(Permit.lead_tier, func.count(Permit.id))
            .where(Permit.lead_tier != "")
            .group_by(Permit.lead_tier)
        )
        by_tier = {tier: count for tier, count in session.exec(tier_stmt).all()}

        # By property type
        prop_stmt = (
            select(Permit.ai_property_type, func.count(Permit.id))
            .where(Permit.ai_property_type != "")
            .group_by(Permit.ai_property_type)
        )
        by_property = {pt: count for pt, count in session.exec(prop_stmt).all()}

        # By project category
        cat_stmt = (
            select(Permit.ai_project_category, func.count(Permit.id))
            .where(Permit.ai_project_category != "")
            .group_by(Permit.ai_project_category)
        )
        by_category = {cat: count for cat, count in session.exec(cat_stmt).all()}

        # Avg lead score
        avg_score = session.exec(
            select(func.avg(Permit.lead_score)).where(Permit.lead_score.is_not(None))  # type: ignore
        ).one()

        # Last ingestion
        last_run = session.exec(
            select(PermitIngestionRun)
            .order_by(col(PermitIngestionRun.created_at).desc())
            .limit(1)
        ).first()

        return {
            "total_permits": total,
            "by_city": by_city,
            "by_tier": by_tier,
            "by_property_type": by_property,
            "by_project_category": by_category,
            "avg_lead_score": round(avg_score, 1) if avg_score else 0,
            "last_ingestion": {
                "run_id": last_run.run_id,
                "city": last_run.source_city,
                "records_fetched": last_run.records_fetched,
                "status": last_run.status,
                "created_at": last_run.created_at.isoformat() if last_run.created_at else None,
            } if last_run else None,
        }


@router.get("/{permit_id}")
async def get_permit(permit_id: int, user: dict = Depends(get_current_user)):
    """Get full permit detail by ID."""
    with Session(engine) as session:
        permit = session.get(Permit, permit_id)
        if not permit:
            return JSONResponse(status_code=404, content={"error": "Permit not found"})

        result = _permit_to_dict(permit)
        # Include full raw_data for detail view
        try:
            result["raw_data"] = json.loads(permit.raw_data)
        except (json.JSONDecodeError, TypeError):
            result["raw_data"] = {}

        return result


@router.get("/runs/list")
async def list_ingestion_runs(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
):
    """List permit ingestion runs."""
    with Session(engine) as session:
        stmt = (
            select(PermitIngestionRun)
            .order_by(col(PermitIngestionRun.created_at).desc())
            .offset(offset)
            .limit(limit)
        )
        runs = session.exec(stmt).all()

        return {
            "data": [
                {
                    "id": r.id,
                    "run_id": r.run_id,
                    "source_city": r.source_city,
                    "source_api": r.source_api,
                    "records_fetched": r.records_fetched,
                    "records_standardized": r.records_standardized,
                    "records_enriched": r.records_enriched,
                    "records_qualified": r.records_qualified,
                    "status": r.status,
                    "error": r.error,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                }
                for r in runs
            ],
            "offset": offset,
            "limit": limit,
        }


def _permit_to_dict(p: Permit) -> dict:
    """Convert Permit model to response dict."""
    tags = []
    try:
        tags = json.loads(p.ai_tags) if p.ai_tags else []
    except (json.JSONDecodeError, TypeError):
        pass

    return {
        "id": p.id,
        "permit_number": p.permit_number,
        "permit_type": p.permit_type,
        "status": p.status,
        "work_description": p.work_description,
        "address": p.address,
        "city": p.city,
        "state": p.state,
        "zip_code": p.zip_code,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "applicant_name": p.applicant_name,
        "contractor_name": p.contractor_name,
        "owner_name": p.owner_name,
        "estimated_cost": p.estimated_cost,
        "fee_paid": p.fee_paid,
        "application_date": p.application_date.isoformat() if p.application_date else None,
        "issue_date": p.issue_date.isoformat() if p.issue_date else None,
        "expiration_date": p.expiration_date.isoformat() if p.expiration_date else None,
        "completion_date": p.completion_date.isoformat() if p.completion_date else None,
        "ai_tags": tags,
        "ai_property_type": p.ai_property_type,
        "ai_project_category": p.ai_project_category,
        "ai_summary": p.ai_summary,
        "lead_score": p.lead_score,
        "lead_tier": p.lead_tier,
        "lead_rationale": p.lead_rationale,
        "source_jurisdiction": p.source_jurisdiction,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
