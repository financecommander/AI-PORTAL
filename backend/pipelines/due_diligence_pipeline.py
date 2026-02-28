"""Due Diligence Pipeline - Multi-agent borrower and deal investigation.

Performs comprehensive due diligence on borrower backgrounds, legal
history, UCC filings, and entity structure. Produces a diligence
summary with risk flags for credit committee review.

Agents:
  1. Entity Investigator - Corporate structure, beneficial ownership, OFAC
  2. Litigation Scanner  - Court records, defaults, judgments, liens
  3. Financial Verifier  - Statement analysis, cash flow verification, tax review
  4. Diligence Reporter  - Consolidated findings and risk flag report
"""

import json
import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.providers.factory import get_provider
from backend.providers.base import ProviderResponse

logger = logging.getLogger(__name__)


class DueDiligencePipeline(BasePipeline):
    """
    4-agent pipeline for borrower and deal due diligence.

    Agents:
      1. Entity Investigator - Corporate structure, ownership, sanctions
      2. Litigation Scanner  - Court records, liens, judgments
      3. Financial Verifier  - Financial statement and tax analysis
      4. Diligence Reporter  - Consolidated risk report
    """

    AGENT_NAMES = [
        "Entity Investigator",
        "Litigation Scanner",
        "Financial Verifier",
        "Diligence Reporter",
    ]

    def __init__(self):
        super().__init__(
            name="Due Diligence Engine",
            description=(
                "Comprehensive borrower due diligence including entity investigation, "
                "litigation scanning, financial verification, and consolidated risk reporting"
            ),
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Entity Investigator", "goal": "Analyze corporate structure, beneficial ownership, and sanctions screening", "model": "gemini-2.5-flash"},
            {"name": "Litigation Scanner", "goal": "Search court records, defaults, judgments, liens, and UCC filings", "model": "gemini-2.5-flash"},
            {"name": "Financial Verifier", "goal": "Analyze financial statements, tax returns, and cash flow verification", "model": "gemini-2.5-flash"},
            {"name": "Diligence Reporter", "goal": "Consolidate findings into risk-flagged due diligence report", "model": "gpt-4o"},
        ]

    def estimate_cost(self, input_length: int) -> float:
        return 0.04

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

        if on_progress:
            await on_progress("pipeline_start", {
                "agents": self.AGENT_NAMES,
                "query": query[:200],
            })

        # ═══ AGENT 1: Entity Investigator ═════════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Entity Investigator"})

        entity_report, a1_tokens = await self._run_entity_investigator(query)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Entity Investigator",
            "input_tokens": a1_tokens.get("input", 0),
            "output_tokens": a1_tokens.get("output", 0),
            "total_tokens": a1_tokens.get("input", 0) + a1_tokens.get("output", 0),
            "cost": a1_tokens.get("cost", 0.0),
            "calls": 1,
            "model": "gemini-2.5-flash",
        })
        total_input_tokens += a1_tokens.get("input", 0)
        total_output_tokens += a1_tokens.get("output", 0)
        total_cost += a1_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Entity Investigator",
                "duration_ms": round(a1_ms, 1),
                "output": entity_report[:500],
            })

        # ═══ AGENT 2: Litigation Scanner ══════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Litigation Scanner"})

        litigation_report, a2_tokens = await self._run_litigation_scanner(query)

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Litigation Scanner",
            "input_tokens": a2_tokens.get("input", 0),
            "output_tokens": a2_tokens.get("output", 0),
            "total_tokens": a2_tokens.get("input", 0) + a2_tokens.get("output", 0),
            "cost": a2_tokens.get("cost", 0.0),
            "calls": 1,
            "model": "gemini-2.5-flash",
        })
        total_input_tokens += a2_tokens.get("input", 0)
        total_output_tokens += a2_tokens.get("output", 0)
        total_cost += a2_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Litigation Scanner",
                "duration_ms": round(a2_ms, 1),
                "output": litigation_report[:500],
            })

        # ═══ AGENT 3: Financial Verifier ══════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Financial Verifier"})

        financial_report, a3_tokens = await self._run_financial_verifier(query)

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Financial Verifier",
            "input_tokens": a3_tokens.get("input", 0),
            "output_tokens": a3_tokens.get("output", 0),
            "total_tokens": a3_tokens.get("input", 0) + a3_tokens.get("output", 0),
            "cost": a3_tokens.get("cost", 0.0),
            "calls": 1,
            "model": "gemini-2.5-flash",
        })
        total_input_tokens += a3_tokens.get("input", 0)
        total_output_tokens += a3_tokens.get("output", 0)
        total_cost += a3_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Financial Verifier",
                "duration_ms": round(a3_ms, 1),
                "output": financial_report[:500],
            })

        # ═══ AGENT 4: Diligence Reporter ═════════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Diligence Reporter"})

        final_report, a4_tokens = await self._run_diligence_reporter(
            query, entity_report, litigation_report, financial_report,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Diligence Reporter",
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
                "agent": "Diligence Reporter",
                "duration_ms": round(a4_ms, 1),
                "output": final_report[:500],
            })

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PipelineResult(
            output=final_report,
            total_tokens=total_input_tokens + total_output_tokens,
            total_cost=round(total_cost, 6),
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={"user_hash": user_hash, "query": query[:200]},
        )

    # ── Agent Implementations ───────────────────────────────────────

    async def _run_entity_investigator(self, query: str) -> tuple[str, dict]:
        """Agent 1: Corporate structure, ownership, and sanctions."""
        provider = get_provider("google")

        system_prompt = (
            "You are a due diligence investigator specializing in entity analysis. "
            "Given borrower/entity information, analyze:\n\n"
            "1. **Entity Structure** - Corporate form (LLC, LP, Corp), state of formation, "
            "operating agreements, organizational chart\n"
            "2. **Beneficial Ownership** - Key principals, ownership percentages, control persons\n"
            "3. **Sanctions & Watchlist Screening** - OFAC SDN, BIS Entity List, PEP status\n"
            "4. **Related Entities** - Affiliates, subsidiaries, related party transactions\n"
            "5. **Background Flags** - Prior bankruptcies, criminal records, regulatory actions\n\n"
            "Flag any findings as GREEN (clear), YELLOW (monitor), or RED (escalate). "
            "If information is limited, note what additional searches are recommended."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_litigation_scanner(self, query: str) -> tuple[str, dict]:
        """Agent 2: Court records, liens, and judgments."""
        provider = get_provider("google")

        system_prompt = (
            "You are a legal due diligence analyst specializing in litigation search. "
            "Given borrower/entity information, analyze:\n\n"
            "1. **Civil Litigation** - Pending/resolved lawsuits as plaintiff or defendant\n"
            "2. **Defaults & Foreclosures** - Prior loan defaults, foreclosure actions, deed-in-lieu\n"
            "3. **Judgments & Liens** - Outstanding judgments, tax liens, mechanic's liens\n"
            "4. **UCC Filings** - Existing security interests, priority of liens\n"
            "5. **Bankruptcy History** - Chapter 7/11/13 filings, discharge status\n"
            "6. **Regulatory Actions** - SEC, CFPB, state AG enforcement actions\n\n"
            "Rate each category as CLEAR, FLAGGED, or CRITICAL. "
            "Provide specific case details where available. "
            "Note what court databases should be searched for full verification."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_financial_verifier(self, query: str) -> tuple[str, dict]:
        """Agent 3: Financial statement and tax analysis."""
        provider = get_provider("google")

        system_prompt = (
            "You are a forensic accountant performing financial due diligence. "
            "Given borrower financial information, analyze:\n\n"
            "1. **Financial Statement Review** - Income statement, balance sheet, cash flow trends\n"
            "2. **Liquidity Analysis** - Current ratio, quick ratio, working capital adequacy\n"
            "3. **Net Worth Verification** - Real estate schedule, personal financial statement review\n"
            "4. **Tax Return Analysis** - Consistency with financials, NOLs, entity-level taxes\n"
            "5. **Cash Flow Sufficiency** - Ability to service existing and proposed debt\n"
            "6. **Red Flags** - Unusual transactions, related party flows, declining trends\n\n"
            "Classify overall financial health as STRONG, ADEQUATE, WEAK, or INSUFFICIENT. "
            "If financial data is not provided, outline what documents are needed."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_diligence_reporter(
        self, query: str, entity_report: str,
        litigation_report: str, financial_report: str,
    ) -> tuple[str, dict]:
        """Agent 4: Consolidated due diligence report."""
        provider = get_provider("openai")

        system_prompt = (
            "You are the Chief Risk Officer at an institutional CRE lender. "
            "Produce a formal Due Diligence Report in Markdown. Structure:\n\n"
            "# Due Diligence Report\n\n"
            "## Executive Summary\n"
            "Overall risk rating (PASS / CONDITIONAL PASS / FAIL) with key findings\n\n"
            "## 1. Entity & Ownership Analysis\n"
            "Summary with risk flags (GREEN/YELLOW/RED)\n\n"
            "## 2. Litigation & Legal Review\n"
            "Summary with risk flags (CLEAR/FLAGGED/CRITICAL)\n\n"
            "## 3. Financial Verification\n"
            "Summary with health rating (STRONG/ADEQUATE/WEAK/INSUFFICIENT)\n\n"
            "## 4. Outstanding Items\n"
            "Checklist of documents/verifications still needed\n\n"
            "## 5. Risk Matrix\n"
            "Table: Risk Category | Finding | Severity | Mitigant\n\n"
            "## 6. Recommendation\n"
            "Proceed / Proceed with Conditions / Decline\n\n"
            "Be thorough but concise. Use tables for the risk matrix."
        )

        user_content = (
            f"Subject:\n{query[:2000]}\n\n"
            f"Entity Investigation:\n{entity_report[:2500]}\n\n"
            f"Litigation Scan:\n{litigation_report[:2500]}\n\n"
            f"Financial Verification:\n{financial_report[:2500]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gpt-4o",
            temperature=0.3,
            max_tokens=4096,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }
