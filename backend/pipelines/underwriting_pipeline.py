"""Underwriting Pipeline - Multi-agent CRE deal analysis.

Full deal underwriting from property details and financials.
Produces investment committee-ready analysis with valuation,
cash flow modeling, structure optimization, and IC memo.

Agents:
  1. Property Analyzer   - Valuation, market comps, cap rate analysis
  2. Cash Flow Modeler   - NOI, DSCR, debt yield projections
  3. Structure Optimizer - LTV, rate, term, and covenant recommendations
  4. Memo Generator      - IC-ready underwriting narrative
"""

import json
import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.providers.factory import get_provider
from backend.providers.base import ProviderResponse

logger = logging.getLogger(__name__)


class UnderwritingPipeline(BasePipeline):
    """
    4-agent pipeline for CRE deal underwriting.

    Agents:
      1. Property Analyzer  - Market comps, cap rate, valuation range
      2. Cash Flow Modeler  - NOI waterfall, DSCR, debt yield
      3. Structure Optimizer - Loan structure recommendations
      4. Memo Generator     - Investment committee memo
    """

    AGENT_NAMES = [
        "Property Analyzer",
        "Cash Flow Modeler",
        "Structure Optimizer",
        "Memo Generator",
    ]

    def __init__(self):
        super().__init__(
            name="Underwriting Engine",
            description=(
                "Full CRE deal underwriting with property valuation, cash flow "
                "modeling, loan structure optimization, and IC memo generation"
            ),
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Property Analyzer", "goal": "Analyze property value, market comps, and cap rate", "model": "gemini-2.5-flash"},
            {"name": "Cash Flow Modeler", "goal": "Build NOI waterfall, DSCR, and debt yield projections", "model": "gemini-2.5-flash"},
            {"name": "Structure Optimizer", "goal": "Recommend optimal loan structure (LTV, rate, term, covenants)", "model": "gemini-2.5-flash"},
            {"name": "Memo Generator", "goal": "Generate investment committee underwriting memo", "model": "gpt-4o"},
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

        # ═══ AGENT 1: Property Analyzer ═══════════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Property Analyzer"})

        property_analysis, a1_tokens = await self._run_property_analyzer(query)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Property Analyzer",
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
                "agent": "Property Analyzer",
                "duration_ms": round(a1_ms, 1),
                "output": property_analysis[:500],
            })

        # ═══ AGENT 2: Cash Flow Modeler ═══════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Cash Flow Modeler"})

        cashflow_analysis, a2_tokens = await self._run_cashflow_modeler(query, property_analysis)

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Cash Flow Modeler",
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
                "agent": "Cash Flow Modeler",
                "duration_ms": round(a2_ms, 1),
                "output": cashflow_analysis[:500],
            })

        # ═══ AGENT 3: Structure Optimizer ═════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Structure Optimizer"})

        structure_analysis, a3_tokens = await self._run_structure_optimizer(
            query, property_analysis, cashflow_analysis,
        )

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Structure Optimizer",
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
                "agent": "Structure Optimizer",
                "duration_ms": round(a3_ms, 1),
                "output": structure_analysis[:500],
            })

        # ═══ AGENT 4: Memo Generator ═════════════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Memo Generator"})

        final_memo, a4_tokens = await self._run_memo_generator(
            query, property_analysis, cashflow_analysis, structure_analysis,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Memo Generator",
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
                "agent": "Memo Generator",
                "duration_ms": round(a4_ms, 1),
                "output": final_memo[:500],
            })

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PipelineResult(
            output=final_memo,
            total_tokens=total_input_tokens + total_output_tokens,
            total_cost=round(total_cost, 6),
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={
                "user_hash": user_hash,
                "query": query[:200],
            },
        )

    # ── Agent Implementations ───────────────────────────────────────

    async def _run_property_analyzer(self, query: str) -> tuple[str, dict]:
        """Agent 1: Analyze property, market comps, and valuation."""
        provider = get_provider("google")

        system_prompt = (
            "You are a senior CRE appraiser and market analyst. Given a deal description, provide:\n\n"
            "1. **Property Summary** - Asset type, location, size, year built, condition\n"
            "2. **Market Analysis** - Submarket fundamentals, vacancy rates, rent trends\n"
            "3. **Comparable Sales** - 3-5 recent comps with $/SF or $/unit and cap rates\n"
            "4. **Valuation Range** - Low/mid/high values using income approach and sales comps\n"
            "5. **Cap Rate Analysis** - Market cap rate, going-in cap, exit cap assumption\n\n"
            "If specific numbers aren't provided, use reasonable market assumptions and state them clearly. "
            "Be quantitative and specific."
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

    async def _run_cashflow_modeler(self, query: str, property_analysis: str) -> tuple[str, dict]:
        """Agent 2: Build cash flow projections."""
        provider = get_provider("google")

        system_prompt = (
            "You are a CRE financial analyst specializing in cash flow modeling. "
            "Using the property analysis and deal info, produce:\n\n"
            "1. **Revenue Projections** - GPR, vacancy/credit loss, concessions, EGI\n"
            "2. **Operating Expenses** - Itemized OpEx (taxes, insurance, mgmt, R&M, utilities)\n"
            "3. **NOI Waterfall** - Year 1 through Year 5 NOI projections\n"
            "4. **Debt Service Coverage** - DSCR at various rate/term scenarios\n"
            "5. **Debt Yield** - Current and stabilized debt yield\n"
            "6. **Key Metrics** - Cash-on-cash return, IRR estimate, equity multiple\n\n"
            "Use tables where possible. If data is missing, state assumptions clearly."
        )

        user_content = (
            f"Deal Description:\n{query[:3000]}\n\n"
            f"Property Analysis:\n{property_analysis[:3000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
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

    async def _run_structure_optimizer(
        self, query: str, property_analysis: str, cashflow_analysis: str,
    ) -> tuple[str, dict]:
        """Agent 3: Recommend optimal loan structure."""
        provider = get_provider("google")

        system_prompt = (
            "You are a CRE debt capital markets specialist. Based on the property analysis "
            "and cash flow model, recommend:\n\n"
            "1. **Recommended LTV** - Max LTV and recommended LTV with rationale\n"
            "2. **Loan Amount** - Recommended proceed based on DSCR and debt yield constraints\n"
            "3. **Rate & Term** - Fixed vs floating, suggested spread, term and amortization\n"
            "4. **Covenants** - Minimum DSCR, debt yield, LTV tests\n"
            "5. **Structure Options** - Senior/mezz split, interest reserve, earn-out provisions\n"
            "6. **Risk Mitigants** - Recourse, guaranties, reserve requirements\n"
            "7. **Pricing Grid** - Rate scenarios (base, stress, severe)\n\n"
            "Be specific with numbers. Reference industry standards for the asset class."
        )

        user_content = (
            f"Deal Description:\n{query[:2000]}\n\n"
            f"Property Analysis:\n{property_analysis[:2000]}\n\n"
            f"Cash Flow Model:\n{cashflow_analysis[:2000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
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

    async def _run_memo_generator(
        self, query: str, property_analysis: str,
        cashflow_analysis: str, structure_analysis: str,
    ) -> tuple[str, dict]:
        """Agent 4: Generate IC underwriting memo."""
        provider = get_provider("openai")

        system_prompt = (
            "You are the head of credit at an institutional CRE lender. Write a formal "
            "Investment Committee Underwriting Memo in Markdown. Structure:\n\n"
            "# Investment Committee Memo\n\n"
            "## 1. Executive Summary\n"
            "Brief deal overview, recommendation (Approve/Decline/Conditional), key metrics\n\n"
            "## 2. Deal Overview\n"
            "Property description, borrower background, transaction summary\n\n"
            "## 3. Property & Market Analysis\n"
            "Location, market fundamentals, competitive set, valuation\n\n"
            "## 4. Financial Analysis\n"
            "NOI, DSCR, debt yield, cash flow projections\n\n"
            "## 5. Proposed Loan Structure\n"
            "Amount, LTV, rate, term, covenants, structure\n\n"
            "## 6. Risk Factors & Mitigants\n"
            "Key risks and how they're addressed\n\n"
            "## 7. Recommendation\n"
            "Final recommendation with conditions\n\n"
            "Be institutional in tone. Use specific numbers throughout."
        )

        user_content = (
            f"Deal Input:\n{query[:2000]}\n\n"
            f"Property Analysis:\n{property_analysis[:2500]}\n\n"
            f"Cash Flow Model:\n{cashflow_analysis[:2500]}\n\n"
            f"Structure Recommendations:\n{structure_analysis[:2500]}"
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
