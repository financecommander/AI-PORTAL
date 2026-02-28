"""Portfolio Monitoring Pipeline - Multi-agent loan surveillance.

Tracks existing loan portfolios for covenant compliance, early
warning signals, and watchlist management. Produces monthly
surveillance reports with escalation recommendations.

Agents:
  1. Covenant Monitor    - DSCR, LTV, debt yield compliance testing
  2. Early Warning Radar - Market deterioration, borrower stress signals
  3. Watchlist Manager   - Risk rating migration, upgrade/downgrade triggers
  4. Surveillance Reporter - Portfolio health dashboard and escalation report
"""

import json
import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.providers.factory import get_provider
from backend.providers.base import ProviderResponse

logger = logging.getLogger(__name__)


class PortfolioMonitoringPipeline(BasePipeline):
    """
    4-agent pipeline for loan portfolio surveillance.

    Agents:
      1. Covenant Monitor    - Financial covenant testing
      2. Early Warning Radar - Stress signals and market triggers
      3. Watchlist Manager   - Risk migration and watchlist actions
      4. Surveillance Reporter - Portfolio dashboard report
    """

    AGENT_NAMES = [
        "Covenant Monitor",
        "Early Warning Radar",
        "Watchlist Manager",
        "Surveillance Reporter",
    ]

    def __init__(self):
        super().__init__(
            name="Portfolio Monitoring Engine",
            description=(
                "Loan portfolio surveillance with covenant compliance testing, "
                "early warning detection, watchlist management, and dashboard reporting"
            ),
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Covenant Monitor", "goal": "Test DSCR, LTV, and debt yield covenant compliance", "model": "gemini-2.5-flash"},
            {"name": "Early Warning Radar", "goal": "Detect market deterioration and borrower stress signals", "model": "gemini-2.5-flash"},
            {"name": "Watchlist Manager", "goal": "Track risk rating migrations and recommend watchlist actions", "model": "gemini-2.5-flash"},
            {"name": "Surveillance Reporter", "goal": "Generate portfolio health dashboard with escalation flags", "model": "gpt-4o"},
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

        # ═══ AGENT 1: Covenant Monitor ════════════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Covenant Monitor"})

        covenant_report, a1_tokens = await self._run_covenant_monitor(query)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Covenant Monitor",
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
                "agent": "Covenant Monitor",
                "duration_ms": round(a1_ms, 1),
                "output": covenant_report[:500],
            })

        # ═══ AGENT 2: Early Warning Radar ═════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Early Warning Radar"})

        warning_report, a2_tokens = await self._run_early_warning(query, covenant_report)

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Early Warning Radar",
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
                "agent": "Early Warning Radar",
                "duration_ms": round(a2_ms, 1),
                "output": warning_report[:500],
            })

        # ═══ AGENT 3: Watchlist Manager ═══════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Watchlist Manager"})

        watchlist_report, a3_tokens = await self._run_watchlist_manager(
            query, covenant_report, warning_report,
        )

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Watchlist Manager",
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
                "agent": "Watchlist Manager",
                "duration_ms": round(a3_ms, 1),
                "output": watchlist_report[:500],
            })

        # ═══ AGENT 4: Surveillance Reporter ═══════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Surveillance Reporter"})

        final_report, a4_tokens = await self._run_surveillance_reporter(
            query, covenant_report, warning_report, watchlist_report,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Surveillance Reporter",
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
                "agent": "Surveillance Reporter",
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

    async def _run_covenant_monitor(self, query: str) -> tuple[str, dict]:
        """Agent 1: Financial covenant compliance testing."""
        provider = get_provider("google")

        system_prompt = (
            "You are a loan surveillance analyst testing covenant compliance. "
            "Given portfolio/loan data, perform:\n\n"
            "1. **DSCR Test** - Current DSCR vs minimum required, trend (3 periods)\n"
            "2. **LTV Test** - Current LTV vs maximum allowed, mark-to-market estimate\n"
            "3. **Debt Yield Test** - Current NOI / outstanding balance vs minimum\n"
            "4. **Payment Status** - Current, 30-day, 60-day, 90+ days delinquent\n"
            "5. **Reserve Status** - Tax, insurance, replacement reserves adequacy\n"
            "6. **Occupancy Test** - Current occupancy vs minimum required\n\n"
            "For each test: PASS, WATCH (within 10% of trigger), BREACH, or N/A. "
            "Include specific numbers. Use a table format."
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

    async def _run_early_warning(self, query: str, covenant_report: str) -> tuple[str, dict]:
        """Agent 2: Market and borrower stress signals."""
        provider = get_provider("google")

        system_prompt = (
            "You are a credit risk early warning analyst. Identify stress signals:\n\n"
            "1. **Market Signals** - Submarket vacancy trends, rent growth deceleration, "
            "new supply pipeline, cap rate expansion\n"
            "2. **Borrower Signals** - Payment pattern changes, reserve draw requests, "
            "modification requests, communication changes\n"
            "3. **Property Signals** - Occupancy decline, tenant rollover risk, "
            "deferred maintenance, capital expenditure needs\n"
            "4. **Macro Signals** - Interest rate environment, regulatory changes, "
            "sector-specific headwinds\n"
            "5. **Trigger Events** - Lease expirations >20% of NRA, anchor tenant departure, "
            "insurance claims, environmental issues\n\n"
            "Rate each signal: GREEN (no concern), YELLOW (monitor), ORANGE (elevated), RED (immediate action). "
            "Provide specific data points where available."
        )

        user_content = (
            f"Portfolio/Loan Data:\n{query[:3000]}\n\n"
            f"Covenant Status:\n{covenant_report[:2000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
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

    async def _run_watchlist_manager(
        self, query: str, covenant_report: str, warning_report: str,
    ) -> tuple[str, dict]:
        """Agent 3: Risk rating migration and watchlist actions."""
        provider = get_provider("google")

        system_prompt = (
            "You are a portfolio risk manager handling watchlist decisions. "
            "Based on covenant testing and early warning signals, determine:\n\n"
            "1. **Current Risk Rating** - Pass (1-4), Special Mention (5), Substandard (6), "
            "Doubtful (7), Loss (8)\n"
            "2. **Rating Migration** - Upgrade, Stable, Downgrade recommendation with rationale\n"
            "3. **Watchlist Action** - Add to Watchlist / Remove from Watchlist / Maintain\n"
            "4. **Required Actions** - Specific follow-up items with deadlines\n"
            "5. **Escalation** - Does this require Credit Committee review? Yes/No with reason\n"
            "6. **Probability of Default** - Low (<5%), Moderate (5-15%), Elevated (15-30%), High (>30%)\n\n"
            "Provide clear rationale for each decision. Reference specific covenant results "
            "and warning signals."
        )

        user_content = (
            f"Portfolio/Loan Data:\n{query[:2000]}\n\n"
            f"Covenant Testing:\n{covenant_report[:2000]}\n\n"
            f"Early Warning Signals:\n{warning_report[:2000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
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

    async def _run_surveillance_reporter(
        self, query: str, covenant_report: str,
        warning_report: str, watchlist_report: str,
    ) -> tuple[str, dict]:
        """Agent 4: Portfolio surveillance dashboard report."""
        provider = get_provider("openai")

        system_prompt = (
            "You are the Head of Portfolio Management at an institutional CRE lender. "
            "Produce a Portfolio Surveillance Report in Markdown. Structure:\n\n"
            "# Portfolio Surveillance Report\n\n"
            "## Executive Summary\n"
            "Overall portfolio health, key concerns, and required actions\n\n"
            "## 1. Covenant Compliance Dashboard\n"
            "Table: Loan | DSCR | LTV | Debt Yield | Occupancy | Status\n\n"
            "## 2. Early Warning Signals\n"
            "Summary of active warnings by severity (RED/ORANGE/YELLOW)\n\n"
            "## 3. Watchlist Update\n"
            "Additions, removals, rating migrations\n\n"
            "## 4. Action Items\n"
            "Prioritized list with owners and deadlines\n\n"
            "## 5. Portfolio Metrics\n"
            "WA DSCR, WA LTV, delinquency rate, watchlist concentration\n\n"
            "## 6. Escalation Summary\n"
            "Items requiring Credit Committee or senior management review\n\n"
            "Use tables and be concise. Focus on actionable insights."
        )

        user_content = (
            f"Portfolio Data:\n{query[:2000]}\n\n"
            f"Covenant Testing:\n{covenant_report[:2500]}\n\n"
            f"Early Warnings:\n{warning_report[:2500]}\n\n"
            f"Watchlist Actions:\n{watchlist_report[:2500]}"
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
