"""Lex Intelligence Ultimate: 6-agent AI orchestration across 4 LLMs.

A sophisticated multi-agent pipeline for comprehensive AI analysis and reasoning.
"""

from __future__ import annotations

from typing import Any


def create_lex_intelligence_crew() -> Any:
    """Create the Lex Intelligence Ultimate crew.
    
    6 agents across 4 LLMs:
    - Strategic Analyst (GPT-4)
    - Research Specialist (Claude-3 Opus)
    - Technical Reviewer (Gemini Pro)
    - Creative Synthesizer (GPT-4 Turbo)
    - Quality Assurance (Claude-3 Sonnet)
    - Executive Summarizer (GPT-4)
    
    Returns:
        Configured CrewAI Crew instance
    """
    try:
        from crewai import Agent, Crew, Task
    except ImportError:
        raise NotImplementedError(
            "CrewAI not available. Install with: pip install crewai"
        )
    
    # Agent 1: Strategic Analyst (GPT-4)
    strategic_analyst = Agent(
        role="Strategic Analyst",
        goal="Analyze input from a strategic perspective and identify key objectives",
        backstory="You are an expert strategic thinker with decades of experience in high-level planning.",
        llm="gpt-4",
        verbose=False,
    )
    
    # Agent 2: Research Specialist (Claude-3 Opus)
    research_specialist = Agent(
        role="Research Specialist",
        goal="Conduct thorough research and gather comprehensive information",
        backstory="You are a meticulous researcher with expertise in data gathering and analysis.",
        llm="claude-3-opus",
        verbose=False,
    )
    
    # Agent 3: Technical Reviewer (Gemini Pro)
    technical_reviewer = Agent(
        role="Technical Reviewer",
        goal="Review technical aspects and ensure accuracy",
        backstory="You are a technical expert who validates information for correctness.",
        llm="gemini-pro",
        verbose=False,
    )
    
    # Agent 4: Creative Synthesizer (GPT-4 Turbo)
    creative_synthesizer = Agent(
        role="Creative Synthesizer",
        goal="Synthesize information creatively and generate innovative solutions",
        backstory="You excel at connecting disparate ideas and creating novel approaches.",
        llm="gpt-4-turbo",
        verbose=False,
    )
    
    # Agent 5: Quality Assurance (Claude-3 Sonnet)
    quality_assurance = Agent(
        role="Quality Assurance",
        goal="Ensure output meets quality standards and is coherent",
        backstory="You are a quality expert who ensures excellence in all deliverables.",
        llm="claude-3-sonnet",
        verbose=False,
    )
    
    # Agent 6: Executive Summarizer (GPT-4)
    executive_summarizer = Agent(
        role="Executive Summarizer",
        goal="Create clear, actionable executive summaries",
        backstory="You specialize in distilling complex information into executive briefs.",
        llm="gpt-4",
        verbose=False,
    )
    
    # Define tasks for each agent
    task_analyze = Task(
        description="Analyze the input: {query}",
        expected_output="Strategic analysis of the input",
        agent=strategic_analyst,
    )
    
    task_research = Task(
        description="Research relevant information based on the analysis",
        expected_output="Comprehensive research findings",
        agent=research_specialist,
    )
    
    task_review = Task(
        description="Review the research for technical accuracy",
        expected_output="Technical validation report",
        agent=technical_reviewer,
    )
    
    task_synthesize = Task(
        description="Synthesize findings into innovative solutions",
        expected_output="Creative synthesis and recommendations",
        agent=creative_synthesizer,
    )
    
    task_qa = Task(
        description="Perform quality assurance on all outputs",
        expected_output="Quality assurance report",
        agent=quality_assurance,
    )
    
    task_summarize = Task(
        description="Create an executive summary of all findings",
        expected_output="Executive summary with actionable insights",
        agent=executive_summarizer,
    )
    
    # Create the crew
    crew = Crew(
        agents=[
            strategic_analyst,
            research_specialist,
            technical_reviewer,
            creative_synthesizer,
            quality_assurance,
            executive_summarizer,
        ],
        tasks=[
            task_analyze,
            task_research,
            task_review,
            task_synthesize,
            task_qa,
            task_summarize,
        ],
        verbose=False,
    )
    
    return crew
