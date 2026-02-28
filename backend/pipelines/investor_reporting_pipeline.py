"""Investor Reporting Pipeline - Multi-agent LP/GP narrative generation.

Generates institutional-quality investor reports from portfolio data.
Produces quarterly/monthly LP letters, fund performance summaries,
attribution analysis, and market commentary.

Agents:
  1. Performance Analyst   - Fund returns, IRR, equity multiples, attribution
  2. Portfolio Narrator    - Asset-level narratives and operational updates
  3. Market Commentator   - Macro outlook, sector themes, risk positioning
  4. Report Assembler     - Final LP letter with compliance and disclosures
"""

import json
import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.providers.factory import get_provider
from backend.providers.base import ProviderResponse

logger = logging.getLogger(__name__)


class InvestorReportingPipeline(BasePipeline):
    """
    4-agent pipeline for investor reporting and LP letter generation.

    Agents:
      1. Performance Analyst  - Fund-level returns and attribution
      2. Portfolio Narrator   - Asset-level updates and narratives
      3. Market Commentator  - Market outlook and positioning
      4. Report Assembler    - Final LP letter with disclosures
    """

    AGENT_NAMES = [
        "Performance Analyst",
        "Portfolio Narrator",
        "Market Commentator",
        "Report Assembler",
    ]

    def __init__(self):
        super().__init__(
            name="Investor Reporting Engine",
            description=(
                "Automated investor reporting with fund performance analysis, "
                "asset-level narratives, market commentary, and LP letter generation"
            ),
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Performance Analyst", "goal": "Calculate fund returns, IRR, equity multiples, and performance attribution", "model": "gemini-2.5-flash"},
            {"name": "Portfolio Narrator", "goal": "Generate asset-level operational narratives and updates", "model": "gemini-2.5-flash"},
            {"name": "Market Commentator", "goal": "Provide macro outlook, sector themes, and market positioning", "model": "gemini-2.5-flash"},
            {"name": "Report Assembler", "goal": "Assemble final LP letter with compliance language and disclosures", "model": "gpt-4o"},
        ]

    def estimate_cost(self, input_length: int) -> float:
        return 0.05

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

        # ═══ AGENT 1: Performance Analyst ═════════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Performance Analyst"})

        perf_report, a1_tokens = await self._run_performance_analyst(query)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Performance Analyst",
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
                "agent": "Performance Analyst",
                "duration_ms": round(a1_ms, 1),
                "output": perf_report[:500],
            })

        # ═══ AGENT 2: Portfolio Narrator ══════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Portfolio Narrator"})

        narrative_report, a2_tokens = await self._run_portfolio_narrator(query, perf_report)

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Portfolio Narrator",
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
                "agent": "Portfolio Narrator",
                "duration_ms": round(a2_ms, 1),
                "output": narrative_report[:500],
            })

        # ═══ AGENT 3: Market Commentator ══════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Market Commentator"})

        market_report, a3_tokens = await self._run_market_commentator(query)

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Market Commentator",
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
                "agent": "Market Commentator",
                "duration_ms": round(a3_ms, 1),
                "output": market_report[:500],
            })

        # ═══ AGENT 4: Report Assembler ════════════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Report Assembler"})

        final_report, a4_tokens = await self._run_report_assembler(
            query, perf_report, narrative_report, market_report,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Report Assembler",
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
                "agent": "Report Assembler",
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

    async def _run_performance_analyst(self, query: str) -> tuple[str, dict]:
        """Agent 1: Fund returns and performance attribution."""
        provider = get_provider("google")

        system_prompt = (
            "You are an institutional fund performance analyst. "
            "Given fund/portfolio data, produce:\n\n"
            "1. **Fund-Level Returns** - Gross and net IRR (QTD, YTD, ITD), equity multiple, "
            "DPI, TVPI, RVPI\n"
            "2. **Benchmark Comparison** - vs NCREIF, ODCE, relevant indices\n"
            "3. **Performance Attribution** - Returns by property type, geography, vintage\n"
            "4. **Cash Flow Summary** - Capital called, distributions, net cash flow\n"
            "5. **NAV Reconciliation** - Beginning NAV, contributions, distributions, "
            "income, appreciation, ending NAV\n"
            "6. **Fee Summary** - Management fees, incentive fees, fund expenses\n\n"
            "Use tables for financial data. If specific data isn't provided, "
            "use reasonable assumptions and label them clearly."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gemini-2.5-flash",
            temperature=0.3,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_portfolio_narrator(self, query: str, perf_report: str) -> tuple[str, dict]:
        """Agent 2: Asset-level narratives."""
        provider = get_provider("google")

        system_prompt = (
            "You are a portfolio manager writing asset-level updates for investors. "
            "For each property/loan in the portfolio, provide:\n\n"
            "1. **Asset Overview** - Property name, type, location, size\n"
            "2. **Operational Update** - Occupancy, rent collections, NOI trend\n"
            "3. **Leasing Activity** - New leases, renewals, expirations, tenant watch\n"
            "4. **Capital Projects** - Renovations, repositioning, value-add progress\n"
            "5. **Valuation Update** - Current value estimate vs basis, unrealized gain/loss\n"
            "6. **Outlook** - Near-term expectations and strategic plan\n\n"
            "Write in professional narrative form suitable for institutional LPs. "
            "Each asset summary should be 3-5 sentences."
        )

        user_content = (
            f"Portfolio Data:\n{query[:3000]}\n\n"
            f"Performance Analysis:\n{perf_report[:2000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gemini-2.5-flash",
            temperature=0.4,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_market_commentator(self, query: str) -> tuple[str, dict]:
        """Agent 3: Market outlook and commentary."""
        provider = get_provider("google")

        system_prompt = (
            "You are a CRE market strategist writing the market commentary section "
            "of an institutional investor letter. Provide:\n\n"
            "1. **Macroeconomic Overview** - GDP, employment, inflation, Fed policy impact on CRE\n"
            "2. **Capital Markets** - Transaction volume, cap rate trends, debt availability, spreads\n"
            "3. **Sector Outlook** - Multifamily, office, industrial, retail fundamentals\n"
            "4. **Key Themes** - Trends shaping the portfolio (e.g., remote work, nearshoring, AI)\n"
            "5. **Risk Positioning** - How the portfolio is positioned for current environment\n"
            "6. **Forward Outlook** - 6-12 month market expectations\n\n"
            "Write in a measured, institutional tone. Be balanced between opportunities and risks."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gemini-2.5-flash",
            temperature=0.4,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_report_assembler(
        self, query: str, perf_report: str,
        narrative_report: str, market_report: str,
    ) -> tuple[str, dict]:
        """Agent 4: Final LP letter with disclosures."""
        provider = get_provider("openai")

        system_prompt = (
            "You are the CIO of a CRE investment firm writing the quarterly LP letter. "
            "Assemble a polished investor report in Markdown. Structure:\n\n"
            "# Quarterly Investor Letter\n\n"
            "## Dear Partners,\n"
            "Opening paragraph: Market context and fund highlights (2-3 sentences)\n\n"
            "## Fund Performance\n"
            "Key metrics table, benchmark comparison, attribution highlights\n\n"
            "## Portfolio Update\n"
            "Asset-level summaries, operational highlights, capital activity\n\n"
            "## Market Commentary\n"
            "Macro environment, sector themes, risk positioning\n\n"
            "## Outlook & Strategy\n"
            "Forward-looking commentary, pipeline, strategic priorities\n\n"
            "## Capital Account Summary\n"
            "Contributions, distributions, ending balance\n\n"
            "---\n"
            "*Important Disclosures: This report is provided for informational purposes only "
            "and does not constitute an offer to sell or solicitation of an offer to buy any "
            "securities. Past performance is not indicative of future results. Returns are "
            "estimated and unaudited.*\n\n"
            "Tone should be confident but measured. Use first-person plural (we/our). "
            "Professional, institutional quality."
        )

        user_content = (
            f"Fund/Portfolio Input:\n{query[:2000]}\n\n"
            f"Performance Analysis:\n{perf_report[:2500]}\n\n"
            f"Asset Narratives:\n{narrative_report[:2500]}\n\n"
            f"Market Commentary:\n{market_report[:2500]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gpt-4o",
            temperature=0.4,
            max_tokens=4096,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }
