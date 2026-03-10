"""Shovels Pipeline - Multi-agent building permit ingestion and lead scoring.

Fetches building permits from open data APIs, standardizes records,
AI-enriches with property tags, and scores leads for outreach.

Uses PipelineContext for structured data flow between agents and
conditional routing (skip agents 2-4 if no permits fetched).

Agents:
  1. Permit Data Ingester   - Fetch raw permits from city APIs
  2. Data Standardizer      - Map raw fields to canonical Permit schema
  3. AI Enricher            - Tag permits (solar, ADU, new-construction, etc.)
  4. Lead Qualifier         - Score leads 0-100 and assign tier
"""

import json
import time
import uuid
import logging
from typing import Optional, Callable, Any
from datetime import datetime, timezone

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult, PipelineContext
from backend.providers.factory import get_provider
from backend.providers.fallback import get_provider_with_fallback
from backend.tools.permits.fetcher import fetch_permits, available_cities

logger = logging.getLogger(__name__)

# ── Field mappings per city ──────────────────────────────────────

CHICAGO_FIELD_MAP = {
    "permit_": "permit_number",
    "permit_type": "permit_type",
    "review_type": "status",
    "work_description": "work_description",
    "street_number": "_street_number",
    "street_direction": "_street_direction",
    "street_name": "_street_name",
    "suffix": "_street_suffix",
    "city": "city",
    "state": "state",
    "zip_code": "zip_code",
    "latitude": "latitude",
    "longitude": "longitude",
    "contact_1_name": "applicant_name",
    "contractor_1_name": "contractor_name",
    "reported_cost": "estimated_cost",
    "amount_paid": "fee_paid",
    "application_start_date": "application_date",
    "issue_date": "issue_date",
    "xcoordinate": "_xcoord",
    "ycoordinate": "_ycoord",
}


def _standardize_chicago_permit(raw: dict) -> dict:
    """Map a single raw Chicago permit to canonical schema."""
    result = {}
    for raw_key, canonical_key in CHICAGO_FIELD_MAP.items():
        if raw_key in raw:
            result[canonical_key] = raw[raw_key]

    # Build address from components
    parts = []
    for k in ("_street_number", "_street_direction", "_street_name", "_street_suffix"):
        if result.get(k):
            parts.append(str(result.pop(k)))
        else:
            result.pop(k, None)
    if parts:
        result["address"] = " ".join(parts)

    # Pop internal fields
    result.pop("_xcoord", None)
    result.pop("_ycoord", None)

    # Set defaults
    result.setdefault("city", "Chicago")
    result.setdefault("state", "IL")
    result["source_jurisdiction"] = "chicago"
    result["raw_data"] = json.dumps(raw)

    # Coerce types
    for float_field in ("estimated_cost", "fee_paid", "latitude", "longitude"):
        if float_field in result and result[float_field] is not None:
            try:
                result[float_field] = float(result[float_field])
            except (ValueError, TypeError):
                result[float_field] = None

    return result


CITY_STANDARDIZERS = {
    "chicago": _standardize_chicago_permit,
}


class ShovelsPipeline(BasePipeline):
    """
    4-agent pipeline for building permit ingestion, enrichment, and lead scoring.

    Uses PipelineContext for structured data flow:
      ctx.structured_data["raw_permits"]  — raw API results (list[dict])
      ctx.structured_data["city"]         — resolved city name
      ctx.structured_data["permits"]      — standardized/enriched/qualified permits

    Conditional routing:
      - 0 permits fetched → skip agents 2, 3, 4
      - 0 standardized → skip agents 3, 4
    """

    AGENT_NAMES = [
        "Permit Data Ingester",
        "Data Standardizer",
        "AI Enricher",
        "Lead Qualifier",
    ]

    def __init__(self):
        super().__init__(
            name="Shovels Engine",
            description=(
                "Building permit ingestion, AI enrichment, and lead scoring. "
                "Fetches permits from open data APIs, standardizes records, "
                "tags with AI, and scores leads for outreach"
            ),
            category="origination",
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Permit Data Ingester", "goal": "Fetch raw permit data from city open data APIs", "model": "deterministic"},
            {"name": "Data Standardizer", "goal": "Map raw permit fields to canonical schema", "model": "deterministic"},
            {"name": "AI Enricher", "goal": "Tag permits with property type and project categories", "model": "ollama/deepseek-r1:14b"},
            {"name": "Lead Qualifier", "goal": "Score leads 0-100 and assign tier (hot/warm/cold)", "model": "gpt-4o-mini"},
        ]

    def estimate_cost(self, input_length: int) -> float:
        return 0.02

    async def execute(
        self,
        query: str,
        user_hash: str,
        on_progress: Optional[Callable[[str, dict], None]] = None,
    ) -> PipelineResult:
        start_time = time.perf_counter()
        agent_breakdown = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        run_id = str(uuid.uuid4())

        # Shared context for all agents
        ctx = PipelineContext(query=query)

        if on_progress:
            await on_progress("pipeline_start", {
                "agents": self.AGENT_NAMES,
                "query": query[:200],
            })

        # ═══ AGENT 1: Permit Data Ingester ═══════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Permit Data Ingester"})

        fetch_summary = await self._run_permit_ingester(ctx)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Permit Data Ingester",
            "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
            "cost": 0.0, "calls": 1, "model": "deterministic",
        })

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Permit Data Ingester",
                "duration_ms": round(a1_ms, 1),
                "output": fetch_summary[:500],
            })

        # Conditional routing: skip all remaining if no permits fetched
        raw_permits = ctx.structured_data.get("raw_permits", [])
        if len(raw_permits) == 0:
            ctx.skip_remaining()

        # ═══ AGENT 2: Data Standardizer ══════════════════════════════
        a2_start = time.perf_counter()
        if ctx.should_skip("Data Standardizer"):
            if on_progress:
                await on_progress("agent_start", {"agent": "Data Standardizer"})
                await on_progress("agent_complete", {
                    "agent": "Data Standardizer",
                    "duration_ms": 0,
                    "output": "[Skipped — no permits to standardize]",
                    "skipped": True,
                })
            agent_breakdown.append({
                "agent": "Data Standardizer",
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "calls": 0, "model": "deterministic",
            })
        else:
            if on_progress:
                await on_progress("agent_start", {"agent": "Data Standardizer"})

            std_summary = self._run_data_standardizer(ctx)

            a2_ms = (time.perf_counter() - a2_start) * 1000
            agent_breakdown.append({
                "agent": "Data Standardizer",
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "calls": 1, "model": "deterministic",
            })

            if on_progress:
                await on_progress("agent_complete", {
                    "agent": "Data Standardizer",
                    "duration_ms": round(a2_ms, 1),
                    "output": std_summary[:500],
                })

            # Conditional routing: skip enrichment+qualification if 0 standardized
            permits = ctx.structured_data.get("permits", [])
            if len(permits) == 0:
                ctx.skip_agent("AI Enricher")
                ctx.skip_agent("Lead Qualifier")

        # ═══ AGENT 3: AI Enricher ════════════════════════════════════
        a3_start = time.perf_counter()
        if ctx.should_skip("AI Enricher"):
            if on_progress:
                await on_progress("agent_start", {"agent": "AI Enricher"})
                await on_progress("agent_complete", {
                    "agent": "AI Enricher",
                    "duration_ms": 0,
                    "output": "[Skipped — no permits to enrich]",
                    "skipped": True,
                })
            agent_breakdown.append({
                "agent": "AI Enricher",
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "calls": 0, "model": "ollama/deepseek-r1:14b",
            })
        else:
            if on_progress:
                await on_progress("agent_start", {"agent": "AI Enricher"})

            a3_tokens = await self._run_ai_enricher(ctx, on_progress=on_progress)

            a3_ms = (time.perf_counter() - a3_start) * 1000
            agent_breakdown.append({
                "agent": "AI Enricher",
                "input_tokens": a3_tokens.get("input", 0),
                "output_tokens": a3_tokens.get("output", 0),
                "total_tokens": a3_tokens.get("input", 0) + a3_tokens.get("output", 0),
                "cost": a3_tokens.get("cost", 0.0),
                "calls": a3_tokens.get("calls", 1),
                "model": a3_tokens.get("model", "deepseek-r1:14b"),
            })
            total_input_tokens += a3_tokens.get("input", 0)
            total_output_tokens += a3_tokens.get("output", 0)
            total_cost += a3_tokens.get("cost", 0.0)

            permits = ctx.structured_data.get("permits", [])
            if on_progress:
                await on_progress("agent_complete", {
                    "agent": "AI Enricher",
                    "duration_ms": round(a3_ms, 1),
                    "output": f"Enriched {len(permits)} permits with AI tags",
                })

        # ═══ AGENT 4: Lead Qualifier ═════════════════════════════════
        a4_start = time.perf_counter()
        if ctx.should_skip("Lead Qualifier"):
            if on_progress:
                await on_progress("agent_start", {"agent": "Lead Qualifier"})
                await on_progress("agent_complete", {
                    "agent": "Lead Qualifier",
                    "duration_ms": 0,
                    "output": "[Skipped — no permits to qualify]",
                    "skipped": True,
                })
            agent_breakdown.append({
                "agent": "Lead Qualifier",
                "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
                "cost": 0.0, "calls": 0, "model": "gpt-4o-mini",
            })
        else:
            if on_progress:
                await on_progress("agent_start", {"agent": "Lead Qualifier"})

            a4_tokens = await self._run_lead_qualifier(ctx, on_progress=on_progress)

            a4_ms = (time.perf_counter() - a4_start) * 1000
            agent_breakdown.append({
                "agent": "Lead Qualifier",
                "input_tokens": a4_tokens.get("input", 0),
                "output_tokens": a4_tokens.get("output", 0),
                "total_tokens": a4_tokens.get("input", 0) + a4_tokens.get("output", 0),
                "cost": a4_tokens.get("cost", 0.0),
                "calls": a4_tokens.get("calls", 1),
                "model": "gpt-4o-mini",
            })
            total_input_tokens += a4_tokens.get("input", 0)
            total_output_tokens += a4_tokens.get("output", 0)
            total_cost += a4_tokens.get("cost", 0.0)

            permits = ctx.structured_data.get("permits", [])
            if on_progress:
                await on_progress("agent_complete", {
                    "agent": "Lead Qualifier",
                    "duration_ms": round(a4_ms, 1),
                    "output": f"Qualified {len(permits)} permits with lead scores",
                })

        # ═══ Save to database ════════════════════════════════════════
        qualified = ctx.structured_data.get("permits", [])
        city = ctx.structured_data.get("city", "unknown")
        saved_count = await self._save_permits(qualified, run_id, city, len(raw_permits))

        # ═══ Build final report ══════════════════════════════════════
        hot = sum(1 for p in qualified if p.get("lead_tier") == "hot")
        warm = sum(1 for p in qualified if p.get("lead_tier") == "warm")
        cold = sum(1 for p in qualified if p.get("lead_tier") == "cold")

        final_report = (
            f"# Shovels Ingestion Report\n\n"
            f"## Summary\n"
            f"- **City**: {city}\n"
            f"- **Run ID**: `{run_id}`\n"
            f"- **Records Fetched**: {len(raw_permits)}\n"
            f"- **Records Standardized**: {len(ctx.structured_data.get('permits', []))}\n"
            f"- **Records Enriched**: {sum(1 for p in qualified if p.get('ai_tags', '[]') != '[]')}\n"
            f"- **Records Qualified**: {sum(1 for p in qualified if p.get('lead_score') is not None)}\n"
            f"- **Records Saved**: {saved_count}\n\n"
            f"## Lead Distribution\n"
            f"| Tier | Count |\n"
            f"|------|-------|\n"
            f"| Hot  | {hot} |\n"
            f"| Warm | {warm} |\n"
            f"| Cold | {cold} |\n\n"
            f"## Sample Hot Leads\n"
        )

        hot_leads = [p for p in qualified if p.get("lead_tier") == "hot"][:5]
        for i, lead in enumerate(hot_leads, 1):
            final_report += (
                f"\n### {i}. {lead.get('address', 'Unknown Address')}\n"
                f"- **Permit**: {lead.get('permit_number', 'N/A')} ({lead.get('permit_type', 'N/A')})\n"
                f"- **Description**: {lead.get('work_description', 'N/A')[:100]}\n"
                f"- **Applicant**: {lead.get('applicant_name', 'N/A')}\n"
                f"- **Est. Cost**: ${lead.get('estimated_cost', 0) or 0:,.0f}\n"
                f"- **Lead Score**: {lead.get('lead_score', 0)}/100\n"
                f"- **Tags**: {lead.get('ai_tags', '[]')}\n"
                f"- **Rationale**: {lead.get('lead_rationale', 'N/A')}\n"
            )

        if not hot_leads:
            final_report += "\nNo hot leads in this batch.\n"

        # Include routing info if agents were skipped
        if ctx.routing:
            final_report += "\n## Routing\n"
            if ctx.routing.get("skip_all"):
                final_report += "- All agents after Ingester were skipped (0 permits fetched)\n"
            elif ctx.routing.get("skip_agents"):
                for skipped in ctx.routing["skip_agents"]:
                    final_report += f"- {skipped} was skipped\n"

        # Include errors if any
        if ctx.errors:
            final_report += "\n## Errors\n"
            for err in ctx.errors:
                final_report += f"- **{err.get('agent', 'Unknown')}**: {err.get('message', '')}\n"

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PipelineResult(
            output=final_report,
            total_tokens=total_input_tokens + total_output_tokens,
            total_cost=round(total_cost, 6),
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={
                "user_hash": user_hash,
                "query": query[:200],
                "run_id": run_id,
                "city": city,
                "records_fetched": len(raw_permits),
                "records_saved": saved_count,
                "hot_leads": hot,
                "warm_leads": warm,
                "cold_leads": cold,
            },
        )

    # ── Agent Implementations ───────────────────────────────────────

    async def _run_permit_ingester(self, ctx: PipelineContext) -> str:
        """Agent 1: Parse query and fetch raw permits from open data APIs.

        Stores in ctx.structured_data:
          - raw_permits: list[dict]
          - city: str
        """
        city = "chicago"  # Default city
        limit = 100
        where = None

        # Parse query for parameters
        q = ctx.query.lower()
        for c in available_cities():
            if c in q:
                city = c
                break

        # Parse limit
        import re
        limit_match = re.search(r'(\d+)\s*(?:permits?|records?|results?)', q)
        if limit_match:
            limit = min(int(limit_match.group(1)), 1000)

        # Parse date filter
        date_match = re.search(r'(?:since|after|from)\s+(\d{4}-\d{2}-\d{2})', q)
        if date_match:
            where = f"issue_date > '{date_match.group(1)}'"
        elif "recent" in q or "latest" in q:
            where = "issue_date > '2024-01-01'"

        # Fetch
        raw_permits = fetch_permits(city, limit=limit, where=where)

        # Store in context
        ctx.structured_data["raw_permits"] = raw_permits
        ctx.structured_data["city"] = city

        summary = (
            f"Fetched {len(raw_permits)} permits from {city} "
            f"(limit={limit}, where={where or 'none'})"
        )
        ctx.set_output("Permit Data Ingester", summary)
        logger.info(summary)

        return summary

    def _run_data_standardizer(self, ctx: PipelineContext) -> str:
        """Agent 2: Map raw permit fields to canonical Permit schema.

        Reads ctx.structured_data["raw_permits"], writes ctx.structured_data["permits"].
        """
        raw_permits = ctx.structured_data.get("raw_permits", [])
        city = ctx.structured_data.get("city", "chicago")

        standardizer = CITY_STANDARDIZERS.get(city)
        if not standardizer:
            ctx.structured_data["permits"] = []
            summary = f"No standardizer available for {city}"
            ctx.set_output("Data Standardizer", summary)
            return summary

        standardized = []
        for raw in raw_permits:
            try:
                std = standardizer(raw)
                if std.get("permit_number") or std.get("address"):
                    standardized.append(std)
            except Exception as e:
                logger.warning("Failed to standardize permit: %s", e)

        ctx.structured_data["permits"] = standardized

        summary = f"Standardized {len(standardized)}/{len(raw_permits)} permits for {city}"
        ctx.set_output("Data Standardizer", summary)
        logger.info(summary)
        return summary

    async def _run_ai_enricher(self, ctx: PipelineContext, on_progress=None) -> dict:
        """Agent 3: Tag permits with AI-generated categories and summaries.

        Reads/mutates ctx.structured_data["permits"] in place.
        """
        permits = ctx.structured_data.get("permits", [])
        if not permits:
            return {"input": 0, "output": 0, "cost": 0.0, "calls": 0, "model": "ollama/deepseek-r1:14b"}

        provider, model = await get_provider_with_fallback(
            primary_model="deepseek-r1:14b",
            fallback_model="gemini-2.5-flash",
        )
        total_tokens = {"input": 0, "output": 0, "cost": 0.0, "calls": 0, "model": model}

        system_prompt = (
            "You are a commercial real estate data analyst. Given building permit records, "
            "classify and tag each permit.\n\n"
            "For each permit, return a JSON array where each element has:\n"
            '  "index": <0-based index of the permit>,\n'
            '  "tags": [list of tags from: "new-construction", "renovation", "demolition", '
            '"addition", "solar", "adu", "roofing", "electrical", "plumbing", "hvac", '
            '"commercial", "residential", "mixed-use", "industrial", "high-value"],\n'
            '  "property_type": one of "single-family", "multi-family", "commercial", '
            '"industrial", "mixed-use", "institutional", "unknown",\n'
            '  "project_category": one of "ground-up", "major-rehab", "minor-rehab", '
            '"tenant-improvement", "maintenance", "systems-upgrade", "unknown",\n'
            '  "summary": one-sentence summary of the work\n\n'
            "Return ONLY the JSON array, no markdown or explanation."
        )

        # Process in batches of 15
        batch_size = 15
        for batch_start in range(0, len(permits), batch_size):
            batch = permits[batch_start:batch_start + batch_size]

            batch_text = ""
            for i, p in enumerate(batch):
                batch_text += (
                    f"[{i}] Permit: {p.get('permit_number', 'N/A')} | "
                    f"Type: {p.get('permit_type', 'N/A')} | "
                    f"Desc: {p.get('work_description', 'N/A')[:150]} | "
                    f"Cost: ${p.get('estimated_cost', 0) or 0:,.0f} | "
                    f"Address: {p.get('address', 'N/A')}\n"
                )

            try:
                enrichment_text, tokens = await self._stream_agent_response(
                    agent_name="AI Enricher",
                    provider=provider,
                    messages=[{"role": "user", "content": batch_text}],
                    model=model,
                    temperature=0.1,
                    max_tokens=2000,
                    system_prompt=system_prompt,
                    on_progress=on_progress,
                )
                total_tokens["input"] += tokens.get("input", 0)
                total_tokens["output"] += tokens.get("output", 0)
                total_tokens["cost"] += tokens.get("cost", 0.0)
                total_tokens["calls"] += 1

                # Parse JSON response
                cleaned = enrichment_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[-1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()

                enrichments = json.loads(cleaned)

                for item in enrichments:
                    idx = item.get("index", -1)
                    if 0 <= idx < len(batch):
                        real_idx = batch_start + idx
                        permits[real_idx]["ai_tags"] = json.dumps(item.get("tags", []))
                        permits[real_idx]["ai_property_type"] = item.get("property_type", "unknown")
                        permits[real_idx]["ai_project_category"] = item.get("project_category", "unknown")
                        permits[real_idx]["ai_summary"] = item.get("summary", "")

            except (json.JSONDecodeError, Exception) as e:
                logger.warning("AI enrichment batch failed: %s", e)
                ctx.errors.append({"agent": "AI Enricher", "message": str(e)})

        ctx.set_output("AI Enricher", f"Enriched {len(permits)} permits")
        return total_tokens

    async def _run_lead_qualifier(self, ctx: PipelineContext, on_progress=None) -> dict:
        """Agent 4: Score and tier each permit as a lead for outreach.

        Reads/mutates ctx.structured_data["permits"] in place.
        """
        permits = ctx.structured_data.get("permits", [])
        if not permits:
            return {"input": 0, "output": 0, "cost": 0.0, "calls": 0}

        provider = get_provider("openai")
        total_tokens = {"input": 0, "output": 0, "cost": 0.0, "calls": 0}

        system_prompt = (
            "You are a CRE lead qualification specialist. Score building permits as outreach leads.\n\n"
            "Consider these factors for scoring (0-100):\n"
            "- **High value** (70-100): New construction, major renovations >$100K, ground-up, "
            "commercial, multi-family, solar installations, ADUs\n"
            "- **Medium value** (40-69): Mid-range renovations, tenant improvements, systems upgrades\n"
            "- **Low value** (0-39): Minor repairs, maintenance, small residential fixes\n\n"
            "For each permit, return a JSON array with:\n"
            '  "index": <0-based index>,\n'
            '  "score": <0-100>,\n'
            '  "tier": "hot" (70+), "warm" (40-69), or "cold" (0-39),\n'
            '  "rationale": one-sentence explanation of the score\n\n'
            "Return ONLY the JSON array."
        )

        batch_size = 20
        for batch_start in range(0, len(permits), batch_size):
            batch = permits[batch_start:batch_start + batch_size]

            batch_text = ""
            for i, p in enumerate(batch):
                batch_text += (
                    f"[{i}] Permit: {p.get('permit_number', 'N/A')} | "
                    f"Type: {p.get('permit_type', 'N/A')} | "
                    f"Desc: {p.get('work_description', 'N/A')[:100]} | "
                    f"Cost: ${p.get('estimated_cost', 0) or 0:,.0f} | "
                    f"Tags: {p.get('ai_tags', '[]')} | "
                    f"Property: {p.get('ai_property_type', 'unknown')} | "
                    f"Category: {p.get('ai_project_category', 'unknown')}\n"
                )

            try:
                qualifier_text, tokens = await self._stream_agent_response(
                    agent_name="Lead Qualifier",
                    provider=provider,
                    messages=[{"role": "user", "content": batch_text}],
                    model="gpt-4o-mini",
                    temperature=0.1,
                    max_tokens=2000,
                    system_prompt=system_prompt,
                    on_progress=on_progress,
                )
                total_tokens["input"] += tokens.get("input", 0)
                total_tokens["output"] += tokens.get("output", 0)
                total_tokens["cost"] += tokens.get("cost", 0.0)
                total_tokens["calls"] += 1

                cleaned = qualifier_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[-1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()

                scores = json.loads(cleaned)

                for item in scores:
                    idx = item.get("index", -1)
                    if 0 <= idx < len(batch):
                        real_idx = batch_start + idx
                        permits[real_idx]["lead_score"] = item.get("score", 0)
                        permits[real_idx]["lead_tier"] = item.get("tier", "cold")
                        permits[real_idx]["lead_rationale"] = item.get("rationale", "")

            except (json.JSONDecodeError, Exception) as e:
                logger.warning("Lead qualification batch failed: %s", e)
                ctx.errors.append({"agent": "Lead Qualifier", "message": str(e)})

        ctx.set_output("Lead Qualifier", f"Qualified {len(permits)} permits")
        return total_tokens

    async def _save_permits(
        self, permits: list[dict], run_id: str, city: str, total_fetched: int,
    ) -> int:
        """Bulk insert permits and create ingestion run record."""
        saved = 0
        try:
            from backend.database import engine
            from backend.models import Permit, PermitIngestionRun
            from sqlmodel import Session

            with Session(engine) as session:
                ingestion_run = PermitIngestionRun(
                    run_id=run_id,
                    source_city=city,
                    source_api=f"{city}_open_data",
                    records_fetched=total_fetched,
                    records_standardized=len(permits),
                    records_enriched=sum(1 for p in permits if p.get("ai_tags", "[]") != "[]"),
                    records_qualified=sum(1 for p in permits if p.get("lead_score") is not None),
                    status="completed",
                )
                session.add(ingestion_run)

                for p in permits:
                    permit = Permit(
                        ingestion_run_id=run_id,
                        permit_number=p.get("permit_number", ""),
                        permit_type=p.get("permit_type", ""),
                        status=p.get("status", ""),
                        work_description=p.get("work_description", ""),
                        address=p.get("address", ""),
                        city=p.get("city", ""),
                        state=p.get("state", ""),
                        zip_code=p.get("zip_code", ""),
                        latitude=p.get("latitude"),
                        longitude=p.get("longitude"),
                        applicant_name=p.get("applicant_name", ""),
                        contractor_name=p.get("contractor_name", ""),
                        owner_name=p.get("owner_name", ""),
                        estimated_cost=p.get("estimated_cost"),
                        fee_paid=p.get("fee_paid"),
                        ai_tags=p.get("ai_tags", "[]"),
                        ai_property_type=p.get("ai_property_type", ""),
                        ai_project_category=p.get("ai_project_category", ""),
                        ai_summary=p.get("ai_summary", ""),
                        lead_score=p.get("lead_score"),
                        lead_tier=p.get("lead_tier", ""),
                        lead_rationale=p.get("lead_rationale", ""),
                        source_jurisdiction=p.get("source_jurisdiction", ""),
                        raw_data=p.get("raw_data", "{}"),
                    )
                    session.add(permit)
                    saved += 1

                session.commit()
                logger.info("Saved %d permits for run %s", saved, run_id)

        except Exception as e:
            logger.error("Failed to save permits: %s", e)

        return saved
