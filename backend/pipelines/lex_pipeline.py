"""Lex Intelligence Pipeline - Multi-agent legal research with aggregation."""

import asyncio
import time
from typing import Optional, Callable, Any
from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.aggregation.lex_aggregation_config import (
    ConvergenceSynthesizer,
    CONVERGENCE_SYSTEM_PROMPT,
    AgentOutput,
    ContentType,
)
from backend.specialists.manager import get_specialist
from backend.providers.factory import get_provider
from backend.utils.token_estimator import calculate_cost, estimate_tokens


# Agent mapping — these are specialist IDs from the specialists config
LEX_AGENTS = {
    1: {"specialist_id": "research-assistant", "role": "Lead Researcher"},
    2: {"specialist_id": "financial-analyst", "role": "Financial Analyst"},
    3: {"specialist_id": "compliance-scanner", "role": "Regulatory Scanner"},
    4: {"specialist_id": "legal-quick", "role": "Legal Quick Consult"},
}

# Agent system prompt addenda
AGENT_PROMPTS = {
    1: """You are the Lead Researcher in the Lex Intelligence Pipeline.
Provide comprehensive research on the query. Structure your response with:
- FACTUAL CLAIMS: Cite specific statutes, dates, case names, regulatory bodies.
- ANALYSIS: Interpret implications, trends, and context.
- RECOMMENDATIONS: Suggest actionable next steps.
Tag each section clearly.""",

    2: """You are the Financial Analyst in the Lex Intelligence Pipeline.
Analyze the financial and market implications of the query. Focus on:
- Quantitative data, market impact, cost-benefit analysis.
- Financial risks and opportunities.
- Revenue and compliance cost projections.
Tag factual claims vs. analysis clearly.""",

    3: """You are the Regulatory Scanner in the Lex Intelligence Pipeline.
Scan for ALL regulatory compliance issues related to the query. Focus on:
- Specific regulations that apply (cite section numbers).
- Potential violations or compliance gaps.
- Required disclosures, licenses, or filings.
Flag every risk — err on the side of caution. Clearly mark risk items.""",

    4: """You are the Legal Quick Consult in the Lex Intelligence Pipeline.
Provide a contrarian legal perspective. Your job is to:
- Challenge the assumptions in the query.
- Identify legal risks others might miss.
- Suggest alternative legal strategies.
Play devil's advocate — if the obvious answer is X, explain why Y might be better.""",
}


class LexPipeline(BasePipeline):
    """Lex Intelligence Pipeline with dual-mode aggregation."""

    def __init__(self):
        super().__init__(
            name="Lex Intelligence",
            description="Multi-agent legal & regulatory research with dual-mode aggregation"
        )

    async def execute(
        self,
        query: str,
        user_hash: str,
        on_progress: Optional[Callable[[str, dict], None]] = None
    ) -> PipelineResult:
        start_time = time.time()

        # Fan out to agents
        agent_outputs = await self._run_agents_parallel(query, on_progress)

        # Synthesize
        synthesizer = ConvergenceSynthesizer()
        synthesized = synthesizer.synthesize(agent_outputs)

        # Final editor call
        final_report = await self._final_editor_call(query, synthesized)

        # Calculate metrics
        duration_ms = (time.time() - start_time) * 1000
        total_tokens = sum(output.get("input_tokens", 0) + output.get("output_tokens", 0) for output in agent_outputs)
        total_cost = sum(output.get("cost_usd", 0) for output in agent_outputs)

        agent_breakdown = [
            {
                "agent_id": output["agent_id"],
                "agent_name": output["agent_name"],
                "input_tokens": output.get("input_tokens", 0),
                "output_tokens": output.get("output_tokens", 0),
                "cost_usd": output.get("cost_usd", 0),
                "latency_ms": output.get("latency_ms", 0),
            }
            for output in agent_outputs
        ]

        return PipelineResult(
            output=final_report,
            total_tokens=total_tokens,
            total_cost=total_cost,
            duration_ms=duration_ms,
            agent_breakdown=agent_breakdown,
            metadata={
                "mechanism_log": synthesized.mechanism_log,
                "expansion_achieved": synthesized.expansion_achieved,
                "agents_used": [LEX_AGENTS[i]["specialist_id"] for i in synthesized.agents_contributing],
            }
        )

    async def _run_agents_parallel(self, query: str, on_progress) -> list[dict]:
        """Run all agents in parallel."""
        tasks = []
        for agent_id, agent_info in LEX_AGENTS.items():
            task = self._call_agent(agent_id, query, on_progress)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        agent_outputs = []
        for i, result in enumerate(results):
            agent_id = list(LEX_AGENTS.keys())[i]
            if isinstance(result, Exception):
                # Log failure but continue
                if on_progress:
                    on_progress("agent_error", {"agent_id": agent_id, "error": str(result)})
                continue
            agent_outputs.append(result)

        return agent_outputs

    async def _call_agent(self, agent_id: int, query: str, on_progress) -> dict:
        """Call a single agent."""
        agent_info = LEX_AGENTS[agent_id]
        specialist_id = agent_info["specialist_id"]
        role = agent_info["role"]
        role_prompt = AGENT_PROMPTS[agent_id]

        specialist = get_specialist(specialist_id)
        provider = get_provider(specialist["provider"])

        system_prompt = specialist.get("system_prompt", "") + "\n\n" + role_prompt

        start_time = time.time()
        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model=specialist["model"],
            temperature=specialist.get("temperature", 0.7),
            max_tokens=specialist.get("max_tokens", 4096),
            system_prompt=system_prompt,
        )
        latency_ms = (time.time() - start_time) * 1000

        # Classify content
        agent_output = classify_content(agent_id, specialist["name"], response.content)

        result = {
            "agent_id": agent_id,
            "agent_name": specialist["name"],
            "raw_response": response.content,
            "agent_output": agent_output,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "latency_ms": latency_ms,
        }

        if on_progress:
            on_progress("agent_complete", {"agent_id": agent_id, "agent_name": specialist["name"]})

        return result

    async def _final_editor_call(self, query: str, synthesized) -> str:
        """Final editor call using Research Assistant."""
        specialist = get_specialist("research-assistant")
        provider = get_provider(specialist["provider"])

        editor_prompt = f"""
        {CONVERGENCE_SYSTEM_PROMPT}

        Original Query: {query}

        Synthesized Content:
        {synthesized.sections}

        Please provide a final, polished report that integrates all the synthesized information.
        """

        response = await provider.send_message(
            messages=[{"role": "user", "content": editor_prompt}],
            model=specialist["model"],
            temperature=specialist.get("temperature", 0.7),
            max_tokens=specialist.get("max_tokens", 4096),
            system_prompt=specialist.get("system_prompt"),
        )

        return response.content

    def get_agents(self) -> list[dict[str, Any]]:
        """Return list of agents in this pipeline."""
        return [
            {
                "id": info["specialist_id"],
                "name": info["role"],
                "role": info["role"],
            }
            for info in LEX_AGENTS.values()
        ]

    def estimate_cost(self, input_length: int) -> float:
        """Estimate cost for given input length."""
        # 4 agents, each with input + output, plus final editor
        estimated_tokens = estimate_tokens("x" * input_length) * 4 * 2 + estimate_tokens("x" * 1000)
        return calculate_cost("gpt-4o", estimated_tokens // 2, estimated_tokens // 2)


def classify_content(agent_id: int, agent_name: str, raw_response: str) -> AgentOutput:
    """
    Parse raw LLM response into classified content blocks.
    """
    lines = raw_response.split('\n')
    blocks = []
    current_type = None
    current_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect section headers
        if "FACTUAL" in line.upper() or "CLAIM" in line.upper():
            if current_content:
                blocks.append({"type": current_type, "content": '\n'.join(current_content), "confidence": 0.8})
                current_content = []
            current_type = ContentType.FACTUAL_CLAIM
        elif "ANALYSIS" in line.upper():
            if current_content:
                blocks.append({"type": current_type, "content": '\n'.join(current_content), "confidence": 0.8})
                current_content = []
            current_type = ContentType.ANALYSIS
        elif "RECOMMEND" in line.upper():
            if current_content:
                blocks.append({"type": current_type, "content": '\n'.join(current_content), "confidence": 0.8})
                current_content = []
            current_type = ContentType.RECOMMENDATION
        elif "RISK" in line.upper():
            if current_content:
                blocks.append({"type": current_type, "content": '\n'.join(current_content), "confidence": 0.8})
                current_content = []
            current_type = ContentType.RISK_ASSESSMENT
        elif "CONTRARIAN" in line.upper() or "ALTERNATIVE" in line.upper():
            if current_content:
                blocks.append({"type": current_type, "content": '\n'.join(current_content), "confidence": 0.8})
                current_content = []
            current_type = ContentType.CONTRARIAN_VIEW
        else:
            if current_type:
                current_content.append(line)

    if current_content:
        blocks.append({"type": current_type or ContentType.ANALYSIS, "content": '\n'.join(current_content), "confidence": 0.8})

    # For agent 3, populate binding_constraints
    binding_constraints = []
    if agent_id == 3:
        if "violation" in raw_response.lower() or "risk" in raw_response.lower():
            binding_constraints.append("regulatory_flag")

    return AgentOutput(
        agent_id=agent_id,
        agent_name=agent_name,
        content_blocks=blocks,
        overall_confidence=0.8,
        binding_constraints=binding_constraints,
    )


def create_lex_pipeline():
    """Factory function for LexPipeline."""
    return LexPipeline()