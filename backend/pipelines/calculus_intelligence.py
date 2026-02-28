"""Calculus Intelligence - 6-agent heterogeneous deep reasoning pipeline.

Designed to match or exceed Grok 4 Heavy on complex reasoning tasks by
leveraging cross-model validation across GPT-4o, Grok, and Gemini.

Architecture:
  Agent 1 (Query Decomposer)      -> GPT-4o   : Classifies complexity, decomposes into subtasks
  Agent 2 (Analytical Reasoner)    -> GPT-4o   : Structured logical reasoning path
  Agent 3 (Creative Reasoner)      -> Grok     : Lateral thinking, unconventional approaches
  Agent 4 (Deep Context Analyst)   -> Gemini   : High-context pattern synthesis
  Agent 5 (Adversarial Validator)  -> GPT-4o   : Cross-validates all paths, finds contradictions
  Agent 6 (Master Synthesizer)     -> Scout    : Final answer with confidence scores, fed all outputs

The key advantage over Grok Heavy: three different model families produce
genuinely different reasoning paths. When they converge, confidence is high.
When they diverge, the validator catches it. A single model family can't do this.
"""

from crewai import Agent, Task, LLM
from backend.pipelines.crew_pipeline import CrewPipeline
from backend.config.settings import settings


def create_calculus_intelligence() -> CrewPipeline:
    """Create Calculus Intelligence deep reasoning pipeline."""

    # --- LLM Configuration (v2.2) — 6-provider diversity ---
    groq_llm = LLM(model="groq/meta-llama/llama-4-scout-17b-16e-instruct", api_key=settings.groq_api_key or "dummy", temperature=0.3, use_native=False)
    gpt_llm = LLM(model="gpt-5.2", api_key=settings.openai_api_key or "dummy", temperature=0.3)
    grok_llm = LLM(model="xai/grok-4-1-fast", api_key=settings.xai_api_key or "dummy", use_native=False)
    gemini_llm = LLM(model="gemini/gemini-3-flash-preview", api_key=settings.google_api_key or "dummy", temperature=0.3, use_native=False)
    deepseek_llm = LLM(model="deepseek/deepseek-reasoner", api_key=settings.deepseek_api_key or "dummy", temperature=0.2, use_native=False)
    claude_llm = LLM(model="anthropic/claude-sonnet-4-5-20250929", api_key=settings.anthropic_api_key or "dummy", temperature=0.2, use_native=False)

    # --- Agent Definitions ---

    # Agent 1: Query Decomposer (Groq/Llama 4 Scout)
    decomposer = Agent(
        role="Query Decomposer & Router",
        goal="Classify query complexity and break it into clear reasoning subtasks",
        backstory=(
            "You are an expert at understanding what makes problems hard. "
            "You assess whether a question requires mathematical reasoning, logical deduction, "
            "creative insight, factual verification, multi-step planning, or domain expertise. "
            "You decompose complex queries into 2-5 clear subtasks that can be independently reasoned about. "
            "You rate overall complexity on a 1-10 scale and identify which reasoning approaches will work best. "
            "You always structure your output clearly so downstream reasoners know exactly what to tackle."
        ),
        llm=groq_llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 2: Analytical Reasoner (GPT-4o)
    analytical_reasoner = Agent(
        role="Analytical Reasoner",
        goal="Produce a rigorous, structured, step-by-step reasoning chain for each subtask",
        backstory=(
            "You are a methodical analytical thinker trained in formal logic, mathematics, and structured problem-solving. "
            "You approach every problem by first identifying premises, then applying deductive reasoning step by step. "
            "You explicitly state assumptions, show your work at every step, and flag uncertainty. "
            "You excel at mathematical proofs, logical arguments, decision analysis, and systematic breakdowns. "
            "You never skip steps or hand-wave over difficult parts. If you are unsure, you say so explicitly "
            "and present multiple possible paths with reasoning for each."
        ),
        llm=gpt_llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 3: Creative Reasoner (Grok)
    creative_reasoner = Agent(
        role="Creative & Lateral Reasoner",
        goal="Generate alternative reasoning paths, unconventional insights, and challenge obvious assumptions",
        backstory=(
            "You are a lateral thinker who approaches problems from angles others miss. "
            "You deliberately challenge the framing of the question itself — is it the right question? "
            "You look for analogies from unrelated domains, consider edge cases, think about what would happen "
            "if key assumptions were reversed, and explore counterintuitive possibilities. "
            "You are not contrarian for its own sake — you genuinely seek insights that structured reasoning misses. "
            "You draw on broad knowledge including science, history, philosophy, and real-world pattern recognition. "
            "When you agree with the analytical path, you say so and explain why from a different angle. "
            "When you disagree, you present a concrete alternative with reasoning."
        ),
        llm=grok_llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 4: Deep Context Analyst (Gemini)
    context_analyst = Agent(
        role="Deep Context Analyst",
        goal="Synthesize all prior reasoning into a coherent picture, identify patterns, and fill gaps",
        backstory=(
            "You are an expert at processing large amounts of information and finding the signal in the noise. "
            "You excel at reading the full output of multiple reasoning agents and identifying: "
            "where they agree (high confidence), where they disagree (needs resolution), "
            "what they all missed (blind spots), and what implicit assumptions are being made. "
            "You have exceptional ability to hold long context and spot subtle connections between ideas. "
            "You synthesize rather than repeat — your output should add new insight, not summarize. "
            "You explicitly map out the agreement/disagreement landscape across reasoning paths."
        ),
        llm=gemini_llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 5: Adversarial Validator (DeepSeek R1)
    validator = Agent(
        role="Adversarial Validator",
        goal="Stress-test all reasoning for logical errors, unsupported claims, contradictions, and blind spots",
        backstory=(
            "You are a rigorous, skeptical validator whose job is to break arguments. "
            "You check every reasoning chain for: logical fallacies, unsupported leaps, "
            "circular reasoning, contradictions between agents, factual claims without evidence, "
            "overconfident conclusions, and missing edge cases. "
            "You assign a confidence score (0-100%) to each major claim based on how well-supported it is. "
            "You are constructive — when you find a flaw, you suggest how to fix it. "
            "If the reasoning is solid, you say so clearly. Do not manufacture objections. "
            "Your output must include: CONFIRMED claims (with confidence), DISPUTED claims (with specific issues), "
            "and MISSING considerations that no agent addressed."
        ),
        llm=deepseek_llm,
        verbose=True,
        allow_delegation=False,
    )

    # Agent 6: Master Synthesizer (Claude)
    synthesizer = Agent(
        role="Master Synthesizer",
        goal="Produce the single authoritative final answer with confidence scores and reasoning transparency, fed all outputs from specialist models",
        backstory=(
            "You are the Master Synthesizer with access to all outputs from the specialist models and raw source documents. "
            "You process vast amounts of information from the decomposer, analytical reasoner, creative reasoner, context analyst, and validator. "
            "You produce higher-quality long-form opinions by maintaining full context across all inputs. "
            "Your output must be: "
            "1) CLEAR — a direct answer to the original question first, then supporting detail. "
            "2) HONEST — explicit confidence levels (high/medium/low) for each major claim. "
            "3) TRANSPARENT — note where the reasoning agents agreed vs disagreed and how you resolved it. "
            "4) COMPLETE — address all subtasks from the decomposition. "
            "5) ACTIONABLE — if the query implies a decision, state what you'd recommend and why. "
            "You leverage your large context window to ensure nothing is missed from the source materials. "
            "You write in clear, direct prose — not academic jargon. "
            "Format with clear sections but prioritize substance over formatting."
        ),
        llm=claude_llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Task Definitions ---

    task1 = Task(
        description=(
            "Analyze the user's query and decompose it for the reasoning pipeline. "
            "Determine: (1) Complexity score 1-10, (2) What types of reasoning are needed "
            "(logical, mathematical, creative, factual, strategic, etc.), "
            "(3) Break the query into 2-5 specific subtasks that can be independently reasoned about, "
            "(4) Identify any key assumptions or ambiguities in the query. "
            "Structure your output clearly with labeled sections."
        ),
        expected_output=(
            "A structured decomposition with complexity score, reasoning types needed, "
            "numbered subtask list, and identified assumptions/ambiguities."
        ),
        agent=decomposer,
    )

    task2 = Task(
        description=(
            "Using the decomposition from Task 1, provide rigorous analytical reasoning for each subtask. "
            "Show your work step by step. For each subtask: state the approach, execute the reasoning, "
            "and state your conclusion with explicit confidence level. "
            "If mathematical, show calculations. If logical, show the argument structure. "
            "If factual, state what you know and what you're uncertain about."
        ),
        expected_output=(
            "Step-by-step analytical reasoning for each subtask with explicit conclusions "
            "and confidence levels. Approximately 500-1000 words."
        ),
        agent=analytical_reasoner,
    )

    task3 = Task(
        description=(
            "Review the decomposition and the analytical reasoning path. Now provide an independent "
            "alternative perspective. Challenge assumptions, explore counterintuitive possibilities, "
            "apply analogies from other domains, and consider edge cases. "
            "Where you agree with the analytical path, explain why from a different angle. "
            "Where you disagree, present a concrete alternative with reasoning. "
            "Think about what everyone else might be missing."
        ),
        expected_output=(
            "An alternative reasoning perspective with specific areas of agreement and disagreement, "
            "novel insights, edge cases, and at least one non-obvious consideration."
        ),
        agent=creative_reasoner,
    )

    task4 = Task(
        description=(
            "You have the decomposition, analytical reasoning, and creative reasoning. "
            "Synthesize these into a coherent picture: "
            "(1) Map where the two reasoning paths AGREE (mark as high-confidence), "
            "(2) Map where they DISAGREE (flag for validation), "
            "(3) Identify BLIND SPOTS — what did both miss?, "
            "(4) Note any implicit assumptions both agents share that might be wrong, "
            "(5) If the creative reasoner raised valid challenges to the analytical path, "
            "assess whether they change the conclusion."
        ),
        expected_output=(
            "A context synthesis mapping agreements, disagreements, blind spots, "
            "and a preliminary assessment of which reasoning path is stronger on each subtask."
        ),
        agent=context_analyst,
    )

    task5 = Task(
        description=(
            "Review ALL prior outputs and perform adversarial validation. For each major claim: "
            "(1) Is it logically sound? Check for fallacies, circular reasoning, unsupported leaps. "
            "(2) Is it supported? Does the reasoning actually prove the claim? "
            "(3) Is it consistent? Do the agents contradict each other? If so, who is right? "
            "(4) Assign confidence (0-100%) to each major conclusion. "
            "Output three lists: CONFIRMED (high-confidence claims), DISPUTED (claims with issues), "
            "and MISSING (things no agent addressed). Be constructive — suggest fixes for flawed reasoning."
        ),
        expected_output=(
            "Validation report with CONFIRMED claims (with confidence %), "
            "DISPUTED claims (with specific issues and suggested fixes), "
            "and MISSING considerations. Be specific, not vague."
        ),
        agent=validator,
    )

    task6 = Task(
        description=(
            "As Scout, the Master Synthesizer, produce the final authoritative answer to the original query. "
            "You have access to all outputs from Tasks 1-5 plus any raw source documents. "
            "Leverage your massive context window to synthesize higher-quality long-form opinions. "
            "Structure your response as: "
            "(1) DIRECT ANSWER — answer the question first in 2-3 sentences, "
            "(2) CONFIDENCE — overall confidence level and per-claim confidence where relevant, "
            "(3) REASONING — the key reasoning chain that supports your answer, "
            "(4) DISAGREEMENTS — note where agents disagreed and how you resolved it, "
            "(5) CAVEATS — what you are less certain about and what would change the answer, "
            "(6) If applicable, RECOMMENDATION — what the user should do. "
            "Ensure nothing is missed from the comprehensive inputs provided."
        ),
        expected_output=(
            "A comprehensive final answer with direct response, confidence assessment, "
            "supporting reasoning, noted disagreements, caveats, and actionable recommendations. "
            "800-1500 words in clear prose, demonstrating higher quality through full synthesis."
        ),
        agent=synthesizer,
    )

    return CrewPipeline(
        name="Calculus Intelligence",
        description="6-agent heterogeneous deep reasoning pipeline with Scout Master Synthesizer fed all outputs",
        agents=[decomposer, analytical_reasoner, creative_reasoner, context_analyst, validator, synthesizer],
        tasks=[task1, task2, task3, task4, task5, task6],
        verbose=True,
    )