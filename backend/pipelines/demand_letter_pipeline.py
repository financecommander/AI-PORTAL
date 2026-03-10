"""Demand Letter Pipeline - Multi-agent legal demand letter generation and review.

Generates professional demand letters for CRE lending scenarios
including loan defaults, covenant breaches, lease violations,
and construction defects.

Uses PipelineContext for full untruncated context passing between agents.

Agents:
  1. Case Analyst      - Analyze situation, identify legal basis and claims
  2. Demand Drafter    - Draft the formal demand letter
  3. Legal Reviewer    - Review for compliance, tone, and enforceability
  4. Final Editor      - Polish, format, and produce final version
"""

import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult, PipelineContext
from backend.providers.factory import get_provider

logger = logging.getLogger(__name__)


# ── System prompts (extracted for readability) ────────────────────

CASE_ANALYST_PROMPT = (
    "You are a senior CRE litigation analyst. Given a dispute or default situation, "
    "perform a thorough case analysis:\n\n"
    "1. **Situation Summary** - Parties involved, timeline, key facts\n"
    "2. **Legal Basis** - Identify applicable legal theories:\n"
    "   - Breach of contract (loan agreement, guaranty, lease)\n"
    "   - Covenant violations (DSCR, LTV, financial reporting)\n"
    "   - Payment default (principal, interest, escrow)\n"
    "   - Construction defect / lien claims\n"
    "   - Fraud / misrepresentation\n"
    "3. **Damages Assessment** - Quantify or estimate damages:\n"
    "   - Outstanding principal and accrued interest\n"
    "   - Default interest and late fees\n"
    "   - Attorney fees and costs\n"
    "   - Consequential damages\n"
    "4. **Cure Period Analysis** - Applicable notice and cure periods from documents\n"
    "5. **Available Remedies** - Foreclosure, acceleration, guaranty enforcement, UCC remedies\n"
    "6. **Risk Assessment** - Strengths and weaknesses of the position\n"
    "7. **Recommended Demand Elements** - What to demand, deadlines, and consequences\n\n"
    "Be specific about applicable law where possible. Note where additional "
    "document review is needed."
)

DEMAND_DRAFTER_PROMPT = (
    "You are an experienced CRE attorney drafting a formal demand letter. "
    "Using the case analysis provided, draft a professional demand letter.\n\n"
    "Follow this structure:\n\n"
    "**LETTERHEAD** (use [FIRM NAME] placeholder)\n\n"
    "**VIA [DELIVERY METHOD]**\n\n"
    "**Date / Addressee**\n\n"
    "**RE: [Subject line with loan/property reference]**\n\n"
    "**Dear [Recipient]:**\n\n"
    "1. **Opening** - Identify the firm, client, and purpose of the letter\n"
    "2. **Background** - Recite relevant facts and contractual relationship\n"
    "3. **Default/Breach** - Specifically identify the default or breach with:\n"
    "   - Reference to specific contract sections\n"
    "   - Timeline of events\n"
    "   - Nature of the violation\n"
    "4. **Damages** - Quantify amounts owed or damages claimed\n"
    "5. **Demand** - State specific demands clearly:\n"
    "   - Payment amount\n"
    "   - Cure actions required\n"
    "   - Deadline (typically 10-30 days)\n"
    "6. **Consequences** - State remedies if demands not met:\n"
    "   - Acceleration of loan\n"
    "   - Foreclosure\n"
    "   - Guaranty enforcement\n"
    "   - Litigation\n"
    "7. **Reservation of Rights** - Preserve all rights and remedies\n"
    "8. **Closing** - Professional close with contact information\n\n"
    "Use formal legal tone. Be firm but professional. "
    "Include specific dollar amounts where provided. "
    "Use [PLACEHOLDER] for unknown details."
)

LEGAL_REVIEWER_PROMPT = (
    "You are a senior partner reviewing a demand letter drafted by a junior associate. "
    "Provide a thorough review covering:\n\n"
    "1. **Legal Accuracy** - Are the legal theories correctly stated? Are contract "
    "references appropriate? Any misstatements of law?\n"
    "2. **Tone Assessment** - Is the tone appropriately firm without being threatening? "
    "Could any language be construed as harassment or bad faith?\n"
    "3. **Completeness** - Are all required elements present? Missing demands? "
    "Missing deadlines? Missing reservation of rights?\n"
    "4. **Enforceability** - Would this letter support or undermine future litigation? "
    "Any admissions or waiver risks?\n"
    "5. **Compliance** - Does it comply with:\n"
    "   - Fair Debt Collection Practices Act (if applicable)\n"
    "   - State-specific notice requirements\n"
    "   - Contractual notice provisions\n"
    "6. **Specific Edits** - List specific changes needed:\n"
    "   - Additions (what to add and where)\n"
    "   - Deletions (what to remove and why)\n"
    "   - Modifications (what to change and suggested language)\n"
    "7. **Risk Flags** - Any statements that could create liability\n"
    "8. **Overall Assessment** - APPROVE / APPROVE WITH CHANGES / REVISE AND RESUBMIT\n\n"
    "Be specific and actionable in your review."
)

FINAL_EDITOR_PROMPT = (
    "You are the final editor producing a client-ready demand letter. "
    "You have the original draft and the senior partner's review comments.\n\n"
    "Your task:\n"
    "1. Incorporate ALL review feedback and specific edits\n"
    "2. Fix any legal inaccuracies identified\n"
    "3. Adjust tone as recommended\n"
    "4. Add any missing elements noted in the review\n"
    "5. Remove any flagged problematic language\n"
    "6. Ensure proper formatting and professional appearance\n\n"
    "Output the FINAL demand letter in Markdown format, ready for printing.\n"
    "After the letter, add a brief section:\n\n"
    "---\n"
    "## Review Summary\n"
    "- Changes incorporated from review\n"
    "- Overall assessment\n"
    "- Recommended next steps after sending\n\n"
    "The letter should be polished, professional, and legally sound."
)


class DemandLetterPipeline(BasePipeline):
    """
    4-agent pipeline for demand letter generation and legal review.

    Uses PipelineContext — each agent reads full untruncated outputs
    from prior agents via ctx.get_output("Agent Name").
    """

    AGENT_NAMES = [
        "Case Analyst",
        "Demand Drafter",
        "Legal Reviewer",
        "Final Editor",
    ]

    def __init__(self):
        super().__init__(
            name="Demand Letter Engine",
            description=(
                "AI-powered demand letter generation with legal analysis, "
                "drafting, compliance review, and final formatting for CRE "
                "lending and real estate disputes"
            ),
            category="legal_execution",
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Case Analyst", "goal": "Analyze the situation and identify legal claims, basis, and damages", "model": "gemini-2.5-flash"},
            {"name": "Demand Drafter", "goal": "Draft a formal demand letter with proper legal structure", "model": "gpt-4o"},
            {"name": "Legal Reviewer", "goal": "Review for legal compliance, tone, enforceability, and risk", "model": "gemini-2.5-flash"},
            {"name": "Final Editor", "goal": "Incorporate review feedback and produce final polished letter", "model": "gpt-4o"},
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

        ctx = PipelineContext(query=query)

        if on_progress:
            await on_progress("pipeline_start", {
                "agents": self.AGENT_NAMES,
                "query": query[:200],
            })

        # ═══ AGENT 1: Case Analyst ═══════════════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Case Analyst"})

        _, a1_tokens = await self._run_agent(
            agent_name="Case Analyst",
            provider=get_provider("google"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": c.query}],
            model="gemini-2.5-flash",
            system_prompt=CASE_ANALYST_PROMPT,
            temperature=0.2,
            max_tokens=3000,
            on_progress=on_progress,
        )

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Case Analyst",
            "input_tokens": a1_tokens.get("input", 0),
            "output_tokens": a1_tokens.get("output", 0),
            "total_tokens": a1_tokens.get("input", 0) + a1_tokens.get("output", 0),
            "cost": a1_tokens.get("cost", 0.0),
            "calls": 1, "model": "gemini-2.5-flash",
        })
        total_input_tokens += a1_tokens.get("input", 0)
        total_output_tokens += a1_tokens.get("output", 0)
        total_cost += a1_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Case Analyst",
                "duration_ms": round(a1_ms, 1),
                "output": ctx.get_output("Case Analyst")[:500],
            })

        # ═══ AGENT 2: Demand Drafter ═════════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Demand Drafter"})

        _, a2_tokens = await self._run_agent(
            agent_name="Demand Drafter",
            provider=get_provider("openai"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": (
                f"Situation:\n{c.query}\n\n"
                f"Case Analysis:\n{c.get_output('Case Analyst')}"
            )}],
            model="gpt-4o",
            system_prompt=DEMAND_DRAFTER_PROMPT,
            temperature=0.3,
            max_tokens=4096,
            on_progress=on_progress,
        )

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Demand Drafter",
            "input_tokens": a2_tokens.get("input", 0),
            "output_tokens": a2_tokens.get("output", 0),
            "total_tokens": a2_tokens.get("input", 0) + a2_tokens.get("output", 0),
            "cost": a2_tokens.get("cost", 0.0),
            "calls": 1, "model": "gpt-4o",
        })
        total_input_tokens += a2_tokens.get("input", 0)
        total_output_tokens += a2_tokens.get("output", 0)
        total_cost += a2_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Demand Drafter",
                "duration_ms": round(a2_ms, 1),
                "output": ctx.get_output("Demand Drafter")[:500],
            })

        # ═══ AGENT 3: Legal Reviewer ═════════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Legal Reviewer"})

        _, a3_tokens = await self._run_agent(
            agent_name="Legal Reviewer",
            provider=get_provider("google"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": (
                f"Original Situation:\n{c.query}\n\n"
                f"Case Analysis:\n{c.get_output('Case Analyst')}\n\n"
                f"Draft Demand Letter:\n{c.get_output('Demand Drafter')}"
            )}],
            model="gemini-2.5-flash",
            system_prompt=LEGAL_REVIEWER_PROMPT,
            temperature=0.2,
            max_tokens=3000,
            on_progress=on_progress,
        )

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Legal Reviewer",
            "input_tokens": a3_tokens.get("input", 0),
            "output_tokens": a3_tokens.get("output", 0),
            "total_tokens": a3_tokens.get("input", 0) + a3_tokens.get("output", 0),
            "cost": a3_tokens.get("cost", 0.0),
            "calls": 1, "model": "gemini-2.5-flash",
        })
        total_input_tokens += a3_tokens.get("input", 0)
        total_output_tokens += a3_tokens.get("output", 0)
        total_cost += a3_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Legal Reviewer",
                "duration_ms": round(a3_ms, 1),
                "output": ctx.get_output("Legal Reviewer")[:500],
            })

        # ═══ AGENT 4: Final Editor ═══════════════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Final Editor"})

        _, a4_tokens = await self._run_agent(
            agent_name="Final Editor",
            provider=get_provider("openai"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": (
                f"Original Situation:\n{c.query}\n\n"
                f"Draft Letter:\n{c.get_output('Demand Drafter')}\n\n"
                f"Legal Review:\n{c.get_output('Legal Reviewer')}"
            )}],
            model="gpt-4o",
            system_prompt=FINAL_EDITOR_PROMPT,
            temperature=0.3,
            max_tokens=4096,
            on_progress=on_progress,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Final Editor",
            "input_tokens": a4_tokens.get("input", 0),
            "output_tokens": a4_tokens.get("output", 0),
            "total_tokens": a4_tokens.get("input", 0) + a4_tokens.get("output", 0),
            "cost": a4_tokens.get("cost", 0.0),
            "calls": 1, "model": "gpt-4o",
        })
        total_input_tokens += a4_tokens.get("input", 0)
        total_output_tokens += a4_tokens.get("output", 0)
        total_cost += a4_tokens.get("cost", 0.0)

        if on_progress:
            await on_progress("agent_complete", {
                "agent": "Final Editor",
                "duration_ms": round(a4_ms, 1),
                "output": ctx.get_output("Final Editor")[:500],
            })

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PipelineResult(
            output=ctx.get_output("Final Editor"),
            total_tokens=total_input_tokens + total_output_tokens,
            total_cost=round(total_cost, 6),
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={"user_hash": user_hash, "query": query[:200]},
        )
