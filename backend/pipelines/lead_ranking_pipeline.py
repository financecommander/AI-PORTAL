"""Lead Ranking Pipeline - Multi-agent lead scoring and risk analysis.

Scores 3rd-party borrower leads using weighted composite scoring
(LTV, Loan Amount, Project Type, Location, Borrower History) and
enriches top-tier leads with AI-powered risk memos.

Agents:
  1. Data Validator   — Parse CSV / extract structured data
  2. Lead Scorer      — Deterministic composite scoring (0-100), Tier 1-4
  3. Risk Analyzer    — Gemini AI risk memos on Tier 1/2 leads
  4. Report Generator — GPT-4o executive summary report
"""

import asyncio
import csv
import io
import json
import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.providers.factory import get_provider
from backend.providers.base import ProviderResponse

logger = logging.getLogger(__name__)


# ── Scoring Constants (from lead_validation_engine.py) ──────────────

TIER_THRESHOLDS = {
    "Tier 1": 80,
    "Tier 2": 60,
    "Tier 3": 40,
    "Tier 4": 0,
}

PROJECT_TYPE_SCORES = {
    "Multifamily": 95,
    "Office": 85,
    "Retail": 75,
    "Industrial": 90,
    "Mixed-Use": 80,
    "Hotel": 70,
    "Senior Housing": 85,
    "Student Housing": 80,
    "Self-Storage": 90,
    "Other": 60,
}

PREMIUM_LOCATIONS = [
    "New York", "San Francisco", "Los Angeles", "Boston", "Seattle",
    "Washington DC", "Chicago", "Miami", "Austin", "Denver",
]

REQUIRED_COLUMNS = [
    "Borrower_ID", "Project_Type", "Loan_Request_Amount",
    "LTV", "Borrower_History_Notes", "Location",
]


# ── Scoring Functions (pure Python, no pandas) ──────────────────────

def score_ltv(ltv) -> float:
    if ltv is None:
        return 50
    ltv = float(ltv)
    if ltv <= 50:
        return 100
    elif ltv <= 65:
        return 90
    elif ltv <= 75:
        return 75
    elif ltv <= 80:
        return 60
    elif ltv <= 90:
        return 40
    else:
        return 20


def score_loan_amount(amount) -> float:
    if amount is None:
        return 50
    amount = float(amount)
    if 1_000_000 <= amount <= 10_000_000:
        return 95
    elif 500_000 <= amount < 1_000_000:
        return 85
    elif 10_000_000 < amount <= 50_000_000:
        return 85
    elif 100_000 <= amount < 500_000:
        return 70
    elif 50_000_000 < amount <= 100_000_000:
        return 70
    elif amount < 100_000:
        return 50
    else:
        return 60


def score_project_type(project_type) -> float:
    if not project_type:
        return 50
    return PROJECT_TYPE_SCORES.get(str(project_type), 60)


def score_location(location) -> float:
    if not location:
        return 50
    loc_lower = str(location).lower()
    for premium in PREMIUM_LOCATIONS:
        if premium.lower() in loc_lower:
            return 95
    return 70


def score_history(notes) -> float:
    if not notes:
        return 50
    lower = str(notes).lower()
    score = 70
    for kw in ["excellent", "strong", "good", "reliable", "consistent",
               "timely", "successful", "proven", "experienced"]:
        if kw in lower:
            score += 5
    for kw in ["default", "late", "poor", "failed", "bankruptcy",
               "foreclosure", "delinquent", "risk", "concern"]:
        if kw in lower:
            score -= 10
    return max(0, min(100, score))


def composite_score(lead: dict) -> float:
    return (
        score_ltv(lead.get("LTV")) * 0.30
        + score_loan_amount(lead.get("Loan_Request_Amount")) * 0.20
        + score_project_type(lead.get("Project_Type")) * 0.20
        + score_location(lead.get("Location")) * 0.15
        + score_history(lead.get("Borrower_History_Notes")) * 0.15
    )


def assign_tier(score: float) -> str:
    if score >= 80:
        return "Tier 1"
    elif score >= 60:
        return "Tier 2"
    elif score >= 40:
        return "Tier 3"
    else:
        return "Tier 4"


# ── CSV Parsing Helpers ─────────────────────────────────────────────

def parse_csv_from_text(text: str) -> list[dict]:
    """Try to parse CSV data from raw text. Returns list of dicts or []."""
    lines = text.strip().split("\n")
    if len(lines) < 2:
        return []
    try:
        reader = csv.DictReader(io.StringIO(text.strip()))
        rows = list(reader)
        if not rows:
            return []
        # Check if any required columns are present
        header_set = set(rows[0].keys())
        if header_set.intersection(set(REQUIRED_COLUMNS)):
            return rows
    except Exception:
        pass
    return []


def coerce_lead_types(lead: dict) -> dict:
    """Convert string values to proper numeric types."""
    result = dict(lead)
    try:
        result["LTV"] = float(result.get("LTV", ""))
    except (ValueError, TypeError):
        result["LTV"] = None
    try:
        val = str(result.get("Loan_Request_Amount", "")).replace(",", "").replace("$", "")
        result["Loan_Request_Amount"] = float(val)
    except (ValueError, TypeError):
        result["Loan_Request_Amount"] = None
    return result


# ── Pipeline Class ──────────────────────────────────────────────────

class LeadRankingPipeline(BasePipeline):
    """
    4-agent pipeline for scoring and ranking 3rd-party borrower leads.

    Agents:
      1. Data Validator  — Parse CSV, validate schema, clean data
      2. Lead Scorer     — Weighted composite scoring (LTV/Loan/Project/Location/History)
      3. Risk Analyzer   — AI risk memos on Tier 1/2 leads (Gemini 2.5 Flash)
      4. Report Generator — Executive summary report (GPT-4o)
    """

    AGENT_NAMES = [
        "Data Validator",
        "Lead Scorer",
        "Risk Analyzer",
        "Report Generator",
    ]

    def __init__(self):
        super().__init__(
            name="Lead Ranking Engine",
            description=(
                "Score and rank 3rd-party borrower leads using weighted composite "
                "scoring (LTV, Loan Amount, Project Type, Location, History) with "
                "AI-powered risk analysis on top-tier leads"
            ),
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Data Validator", "goal": "Parse and validate CSV lead data", "model": "gpt-4o-mini"},
            {"name": "Lead Scorer", "goal": "Apply composite scoring (0-100) and assign Tier 1-4", "model": "deterministic"},
            {"name": "Risk Analyzer", "goal": "Generate AI risk memos for Tier 1/2 leads", "model": "local-ternary / gemini-2.5-flash"},
            {"name": "Report Generator", "goal": "Synthesize executive lead ranking report", "model": "gpt-4o"},
        ]

    def estimate_cost(self, input_length: int) -> float:
        # Rough estimate: ~$0.01-0.05 per run depending on lead count
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

        # ── pipeline_start ──
        if on_progress:
            await on_progress("pipeline_start", {
                "agents": self.AGENT_NAMES,
                "query": query[:200],
            })

        # ═══ AGENT 1: Data Validator ═════════════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Data Validator"})

        leads, validation_report, a1_tokens = await self._run_data_validator(query)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Data Validator",
            "input_tokens": a1_tokens.get("input", 0),
            "output_tokens": a1_tokens.get("output", 0),
            "total_tokens": a1_tokens.get("input", 0) + a1_tokens.get("output", 0),
            "cost": a1_tokens.get("cost", 0.0),
            "calls": 1,
            "model": a1_tokens.get("model", "csv-parser"),
        })
        total_input_tokens += a1_tokens.get("input", 0)
        total_output_tokens += a1_tokens.get("output", 0)
        total_cost += a1_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Data Validator",
                "duration_ms": round(a1_ms, 1),
                "output": validation_report[:500],
            })

        if not leads:
            error_msg = f"Data Validation Failed: {validation_report}"
            if on_progress:
                await on_progress("error", {"message": error_msg})
            raise ValueError(error_msg)

        # ═══ AGENT 2: Lead Scorer ════════════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Lead Scorer"})

        scored_leads, scoring_summary = self._run_lead_scorer(leads)

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Lead Scorer",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost": 0.0,
            "calls": 0,
            "model": "deterministic",
        })

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Lead Scorer",
                "duration_ms": round(a2_ms, 1),
                "output": scoring_summary[:500],
            })

        # ═══ AGENT 3: Risk Analyzer ═════════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Risk Analyzer"})

        scored_leads, risk_summary, a3_tokens = await self._run_risk_analyzer(scored_leads)

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Risk Analyzer",
            "input_tokens": a3_tokens.get("input", 0),
            "output_tokens": a3_tokens.get("output", 0),
            "total_tokens": a3_tokens.get("input", 0) + a3_tokens.get("output", 0),
            "cost": a3_tokens.get("cost", 0.0),
            "calls": a3_tokens.get("calls", 0),
            "model": a3_tokens.get("model", "unknown"),
        })
        total_input_tokens += a3_tokens.get("input", 0)
        total_output_tokens += a3_tokens.get("output", 0)
        total_cost += a3_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Risk Analyzer",
                "duration_ms": round(a3_ms, 1),
                "output": risk_summary[:500],
            })

        # ═══ AGENT 4: Report Generator ══════════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Report Generator"})

        final_report, a4_tokens = await self._run_report_generator(
            query, scored_leads, scoring_summary, risk_summary,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Report Generator",
            "input_tokens": a4_tokens.get("input", 0),
            "output_tokens": a4_tokens.get("output", 0),
            "total_tokens": a4_tokens.get("input", 0) + a4_tokens.get("output", 0),
            "cost": a4_tokens.get("cost", 0.0),
            "calls": 1,
            "model": "gpt-4o",
        })
        total_input_tokens += a4_tokens.get("input", 0)
        total_output_tokens += a4_tokens.get("output", 0)
        total_cost += a4_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Report Generator",
                "duration_ms": round(a4_ms, 1),
                "output": final_report[:500],
            })

        # ── Build result ──
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
                "leads_processed": len(scored_leads),
            },
        )

    # ── Agent Implementations ───────────────────────────────────────

    async def _run_data_validator(
        self, query: str,
    ) -> tuple[list[dict], str, dict]:
        """Agent 1: Parse CSV from query text, or use LLM extraction."""
        tokens: dict[str, Any] = {"input": 0, "output": 0, "cost": 0.0, "model": "csv-parser"}

        # Try direct CSV parsing first
        leads = parse_csv_from_text(query)

        if leads:
            leads = [coerce_lead_types(lead) for lead in leads]
            present = set(leads[0].keys())
            missing = set(REQUIRED_COLUMNS) - present
            if missing:
                report = f"CSV parsed but missing required columns: {missing}"
                return [], report, tokens
            report = f"Successfully parsed {len(leads)} leads from CSV. Columns: {', '.join(sorted(present))}"
            return leads, report, tokens

        # Fallback: LLM extraction from natural language
        try:
            provider = get_provider("openai")
        except Exception as e:
            return [], f"Cannot parse input as CSV and OpenAI provider unavailable: {e}", tokens

        system_prompt = (
            "You are a data extraction specialist. The user will provide text that "
            "contains information about borrower leads. Extract the data into a JSON "
            "array of objects, each with these keys: Borrower_ID, Project_Type, "
            "Loan_Request_Amount (numeric), LTV (numeric 0-100), "
            "Borrower_History_Notes (string), Location (string).\n\n"
            "If the text doesn't contain lead data, return an empty array [].\n"
            "Return ONLY valid JSON, no markdown."
        )

        response: ProviderResponse = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=4096,
            system_prompt=system_prompt,
        )

        tokens = {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
            "model": "gpt-4o-mini",
        }

        try:
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            extracted = json.loads(text)
            if not isinstance(extracted, list) or not extracted:
                return [], "LLM could not extract lead data from the query.", tokens
            leads = [coerce_lead_types(lead) for lead in extracted]
            report = f"Extracted {len(leads)} leads via AI parsing."
            return leads, report, tokens
        except (json.JSONDecodeError, KeyError) as e:
            return [], f"Failed to parse LLM extraction output: {e}", tokens

    def _run_lead_scorer(self, leads: list[dict]) -> tuple[list[dict], str]:
        """Agent 2: Apply composite scoring. Pure computation, no LLM."""
        for lead in leads:
            score = composite_score(lead)
            lead["Composite_Score"] = round(score, 2)
            lead["Institutional_Rating"] = assign_tier(score)

        scores = [l["Composite_Score"] for l in leads]
        tier_counts: dict[str, int] = {}
        for lead in leads:
            tier = lead["Institutional_Rating"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        avg = sum(scores) / len(scores) if scores else 0
        summary = (
            f"Scored {len(leads)} leads. "
            f"Average Score: {avg:.1f}. "
            f"Tier Distribution: {json.dumps(tier_counts)}"
        )
        return leads, summary

    async def _run_risk_analyzer(
        self, leads: list[dict],
    ) -> tuple[list[dict], str, dict]:
        """Agent 3: Generate AI risk memos for Tier 1/2 leads.

        Provider priority:
          1. Local ternary model (zero cost, on-device)
          2. Google Gemini API (cloud fallback)
          3. Skip analysis (if both unavailable)
        """
        tokens: dict[str, Any] = {"input": 0, "output": 0, "cost": 0.0, "calls": 0}

        tier12 = [l for l in leads if l.get("Institutional_Rating") in ("Tier 1", "Tier 2")]

        if not tier12:
            for lead in leads:
                lead["Risk_Flag"] = "Not Analyzed"
                lead["Audit_Memo"] = "N/A - Below Tier 2"
            return leads, "No Tier 1/2 leads to analyze.", tokens

        # Try local ternary model first (zero cost), fall back to Gemini
        provider = None
        model_name = "gemini-2.5-flash"

        try:
            provider = get_provider("local")
            model_name = "local-ternary"
            logger.info("Risk Analyzer: using local ternary model")
        except Exception:
            try:
                provider = get_provider("google")
                logger.info("Risk Analyzer: using Google Gemini")
            except Exception as e:
                logger.warning(f"No risk analysis provider available: {e}")
                for lead in leads:
                    lead["Risk_Flag"] = "Not Analyzed"
                    lead["Audit_Memo"] = "No risk analysis provider configured"
                return leads, "Risk analysis skipped (no provider available).", tokens

        system_prompt = (
            "You are an independent credit risk auditor. Review these borrower notes. "
            "Summarize the borrower's 'Execution Risk' in one sentence and assign a "
            "'Risk Flag' (Low, Medium, High). "
            'Return response in JSON format with keys: "Risk_Flag" and "Audit_Memo".'
        )

        analyzed_count = 0
        for lead in leads:
            if lead.get("Institutional_Rating") not in ("Tier 1", "Tier 2"):
                lead["Risk_Flag"] = "Not Analyzed"
                lead["Audit_Memo"] = "N/A - Below Tier 2"
                continue

            notes = lead.get("Borrower_History_Notes", "")
            if not notes:
                lead["Risk_Flag"] = "Not Analyzed"
                lead["Audit_Memo"] = "No history notes provided"
                continue

            try:
                response = await provider.send_message(
                    messages=[{"role": "user", "content": f"Borrower Notes:\n{notes}"}],
                    model=model_name,
                    temperature=0.2,
                    max_tokens=512,
                    system_prompt=system_prompt,
                )

                tokens["input"] += response.input_tokens
                tokens["output"] += response.output_tokens
                tokens["cost"] += response.cost_usd
                tokens["calls"] += 1

                text = response.content.strip()
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                result = json.loads(text)
                lead["Risk_Flag"] = result.get("Risk_Flag", "Error")
                lead["Audit_Memo"] = result.get("Audit_Memo", "Parse error")
                analyzed_count += 1

            except Exception as e:
                logger.warning(f"Risk analysis failed for {lead.get('Borrower_ID')}: {e}")
                lead["Risk_Flag"] = "Error"
                lead["Audit_Memo"] = f"Analysis failed: {str(e)[:100]}"

        summary = f"Analyzed {analyzed_count}/{len(tier12)} Tier 1/2 leads via {model_name}."
        tokens["model"] = model_name
        return leads, summary, tokens

    async def _run_report_generator(
        self,
        original_query: str,
        scored_leads: list[dict],
        scoring_summary: str,
        risk_summary: str,
    ) -> tuple[str, dict]:
        """Agent 4: Generate executive report using GPT-4o."""
        provider = get_provider("openai")

        leads_table = json.dumps(scored_leads, indent=2, default=str)

        system_prompt = (
            "You are an institutional credit analyst preparing an executive lead ranking report. "
            "Produce a clear, structured Markdown report with:\n"
            "1. **Executive Summary** - Overall findings in 2-3 sentences\n"
            "2. **Tier Distribution** - Table showing lead counts per tier\n"
            "3. **Top Leads (Tier 1)** - Detail on highest-scoring leads with risk flags\n"
            "4. **Risk Alerts** - Any Medium/High risk flags requiring attention\n"
            "5. **Recommendations** - Actionable next steps\n\n"
            "Be concise but thorough. Use the scored data provided."
        )

        user_content = (
            f"Original Request: {original_query[:500]}\n\n"
            f"Scoring Summary: {scoring_summary}\n\n"
            f"Risk Analysis: {risk_summary}\n\n"
            f"Full Scored Data:\n{leads_table[:8000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gpt-4o",
            temperature=0.4,
            max_tokens=4096,
            system_prompt=system_prompt,
        )

        tokens = {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

        return response.content, tokens
