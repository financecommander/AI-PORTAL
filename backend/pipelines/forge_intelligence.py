"""Forge Intelligence — Multi-agent code generation and software engineering pipeline.

Produces software architecture, code generation, code review,
and technical documentation from natural language requirements.

Uses PipelineContext for full untruncated context passing between agents.

Agents:
  1. Requirements Analyst  - Parse requirements, identify components, define scope
  2. Code Architect        - Design system architecture and generate code
  3. Code Reviewer         - Review for bugs, security, and best practices
  4. Documentation Writer  - Produce technical docs and usage guides
"""

import time
import logging
from typing import Optional, Callable, Any

from backend.pipelines.base_pipeline import BasePipeline, PipelineResult, PipelineContext
from backend.providers.factory import get_provider

logger = logging.getLogger(__name__)


# ── System prompts ───────────────────────────────────────────────

REQUIREMENTS_PROMPT = (
    "You are a senior software architect and requirements analyst. "
    "Given a natural language description of a software project or feature, produce:\n\n"
    "1. **Requirements Summary** - Functional and non-functional requirements\n"
    "2. **Components** - Key modules, services, or classes needed\n"
    "3. **Data Model** - Entities and their relationships\n"
    "4. **API Surface** - Endpoints or interfaces if applicable\n"
    "5. **Tech Stack Recommendation** - Languages, frameworks, libraries\n"
    "6. **Scope & Constraints** - What's in/out of scope, known constraints\n"
    "7. **Edge Cases** - Potential edge cases to handle\n\n"
    "Be specific and actionable. Think like a tech lead planning a sprint."
)

ARCHITECT_PROMPT = (
    "You are a principal software engineer. Using the requirements analysis, "
    "produce production-quality code and architecture.\n\n"
    "Structure your output:\n\n"
    "## Architecture Overview\n"
    "Brief description of the system design and patterns used.\n\n"
    "## File Structure\n"
    "```\nproject/\n  src/\n    ...\n```\n\n"
    "## Implementation\n"
    "For each file, provide the complete code in fenced code blocks "
    "with the filename as the language tag:\n\n"
    "```python:src/main.py\n# code here\n```\n\n"
    "Guidelines:\n"
    "- Write clean, idiomatic, production-quality code\n"
    "- Include proper error handling and input validation\n"
    "- Use type hints (Python) or TypeScript types\n"
    "- Follow SOLID principles\n"
    "- Include docstrings and inline comments for complex logic\n"
    "- Minimize dependencies\n"
    "- Write testable code"
)

REVIEWER_PROMPT = (
    "You are a senior code reviewer specializing in security and quality. "
    "Review the generated code and provide:\n\n"
    "1. **Security Review**\n"
    "   - SQL injection, XSS, CSRF vulnerabilities\n"
    "   - Authentication/authorization issues\n"
    "   - Input validation gaps\n"
    "   - Secrets management\n\n"
    "2. **Code Quality**\n"
    "   - Design pattern adherence\n"
    "   - DRY violations\n"
    "   - Error handling completeness\n"
    "   - Edge case coverage\n\n"
    "3. **Performance**\n"
    "   - N+1 queries\n"
    "   - Missing indexes\n"
    "   - Unnecessary allocations\n"
    "   - Async/concurrency issues\n\n"
    "4. **Specific Fixes**\n"
    "   For each issue found, provide:\n"
    "   - File and line reference\n"
    "   - Severity: CRITICAL / HIGH / MEDIUM / LOW\n"
    "   - Suggested fix with code snippet\n\n"
    "5. **Overall Assessment**\n"
    "   PASS / PASS WITH CHANGES / FAIL\n\n"
    "Be thorough but constructive."
)

DOCUMENTATION_PROMPT = (
    "You are a technical writer producing a complete project deliverable. "
    "Combine the architecture, code, and review into a polished output.\n\n"
    "Structure:\n\n"
    "# Project Deliverable\n\n"
    "## 1. Overview\n"
    "Project description and purpose.\n\n"
    "## 2. Architecture\n"
    "System design diagram (ASCII) and component description.\n\n"
    "## 3. Implementation\n"
    "Complete, reviewed code incorporating all feedback from the code review. "
    "Fix any issues identified by the reviewer.\n\n"
    "## 4. Setup & Installation\n"
    "Step-by-step setup instructions.\n\n"
    "## 5. Usage Guide\n"
    "How to use the system with examples.\n\n"
    "## 6. API Reference\n"
    "If applicable, document all endpoints/interfaces.\n\n"
    "## 7. Testing\n"
    "Test plan and example test cases.\n\n"
    "## 8. Review Notes\n"
    "Summary of code review findings and how they were addressed.\n\n"
    "Make the deliverable professional and ready for handoff."
)


class ForgeIntelligence(BasePipeline):
    """
    4-agent pipeline for code generation and software engineering.

    Uses PipelineContext — each agent reads full untruncated outputs
    from prior agents via ctx.get_output("Agent Name").
    """

    AGENT_NAMES = [
        "Requirements Analyst",
        "Code Architect",
        "Code Reviewer",
        "Documentation Writer",
    ]

    def __init__(self):
        super().__init__(
            name="Forge Intelligence",
            description=(
                "Multi-agent code generation pipeline: requirements analysis, "
                "architecture design, code review, and technical documentation"
            ),
            category="intelligence_core",
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Requirements Analyst", "goal": "Parse requirements, identify components, and define scope", "model": "gemini-2.5-flash"},
            {"name": "Code Architect", "goal": "Design system architecture and generate production code", "model": "gpt-4o"},
            {"name": "Code Reviewer", "goal": "Review code for bugs, security vulnerabilities, and best practices", "model": "gemini-2.5-flash"},
            {"name": "Documentation Writer", "goal": "Produce technical documentation and usage guides", "model": "gpt-4o"},
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

        # ═══ AGENT 1: Requirements Analyst ═══════════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Requirements Analyst"})

        _, a1_tokens = await self._run_agent(
            agent_name="Requirements Analyst",
            provider=get_provider("google"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": c.query}],
            model="gemini-2.5-flash",
            system_prompt=REQUIREMENTS_PROMPT,
            temperature=0.2,
            max_tokens=3000,
            on_progress=on_progress,
        )

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Requirements Analyst",
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
                "agent": "Requirements Analyst",
                "duration_ms": round(a1_ms, 1),
                "output": ctx.get_output("Requirements Analyst")[:500],
            })

        # ═══ AGENT 2: Code Architect ═════════════════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Code Architect"})

        _, a2_tokens = await self._run_agent(
            agent_name="Code Architect",
            provider=get_provider("openai"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": (
                f"Request:\n{c.query}\n\n"
                f"Requirements Analysis:\n{c.get_output('Requirements Analyst')}"
            )}],
            model="gpt-4o",
            system_prompt=ARCHITECT_PROMPT,
            temperature=0.3,
            max_tokens=4096,
            on_progress=on_progress,
        )

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Code Architect",
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
                "agent": "Code Architect",
                "duration_ms": round(a2_ms, 1),
                "output": ctx.get_output("Code Architect")[:500],
            })

        # ═══ AGENT 3: Code Reviewer ══════════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Code Reviewer"})

        _, a3_tokens = await self._run_agent(
            agent_name="Code Reviewer",
            provider=get_provider("google"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": (
                f"Original Request:\n{c.query}\n\n"
                f"Requirements:\n{c.get_output('Requirements Analyst')}\n\n"
                f"Generated Code:\n{c.get_output('Code Architect')}"
            )}],
            model="gemini-2.5-flash",
            system_prompt=REVIEWER_PROMPT,
            temperature=0.2,
            max_tokens=3000,
            on_progress=on_progress,
        )

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Code Reviewer",
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
                "agent": "Code Reviewer",
                "duration_ms": round(a3_ms, 1),
                "output": ctx.get_output("Code Reviewer")[:500],
            })

        # ═══ AGENT 4: Documentation Writer ═══════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Documentation Writer"})

        _, a4_tokens = await self._run_agent(
            agent_name="Documentation Writer",
            provider=get_provider("openai"),
            context=ctx,
            build_messages=lambda c: [{"role": "user", "content": (
                f"Request:\n{c.query}\n\n"
                f"Requirements:\n{c.get_output('Requirements Analyst')}\n\n"
                f"Architecture & Code:\n{c.get_output('Code Architect')}\n\n"
                f"Code Review:\n{c.get_output('Code Reviewer')}"
            )}],
            model="gpt-4o",
            system_prompt=DOCUMENTATION_PROMPT,
            temperature=0.3,
            max_tokens=4096,
            on_progress=on_progress,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Documentation Writer",
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
                "agent": "Documentation Writer",
                "duration_ms": round(a4_ms, 1),
                "output": ctx.get_output("Documentation Writer")[:500],
            })

        duration_ms = (time.perf_counter() - start_time) * 1000

        return PipelineResult(
            output=ctx.get_output("Documentation Writer"),
            total_tokens=total_input_tokens + total_output_tokens,
            total_cost=round(total_cost, 6),
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={"user_hash": user_hash, "query": query[:200]},
        )
