"""Lex Intelligence Ultimate - 6-agent legal research pipeline.

Architecture (v3 — optimized for cost, token efficiency & speed):
  Agent 1 (Legal Research Specialist) -> GPT-4.1-mini : Tool-based case law search (cheap, fast)
  Agent 2 (Statutory Analyst)         -> DeepSeek R1  : Deep reasoning on statutes
  Agent 3 (Constitutional Expert)     -> DeepSeek R1  : Deep reasoning on constitutional law
  Agent 4 (Contract Specialist)       -> Grok 4.1 Fast: Fast commercial law analysis (2M ctx)
  Agent 5 (Litigation Strategy)       -> Gemini 3 Flash: Strategy synthesis
  Agent 6 (Master Synthesizer)        -> Claude 4.6   : Final legal opinion (best synthesis)

Token optimizations:
  - Tasks 2-4 only receive Task 1 context (not each other) to prevent bloat
  - Task 5 receives Tasks 1-4 context for full strategic picture
  - Task 6 receives ALL Tasks 1-5 for comprehensive synthesis
  - Agent output limits via max_tokens to cap runaway generations
  - Search agent uses GPT-4.1-mini instead of GPT-5.2 (90% cheaper)
"""

import requests
from typing import Optional
from crewai import Agent, Task, LLM
from crewai.tools import BaseTool
from pydantic import Field
from backend.pipelines.crew_pipeline import CrewPipeline
from backend.config.settings import settings


class LegalSearchTool(BaseTool):
    """Tool for searching legal cases via CourtListener API."""
    
    name: str = "legal_search"
    description: str = "Search for legal cases, precedents, and judicial opinions using CourtListener API"
    api_key: str = Field(default="")
    
    def _run(self, query: str) -> str:
        """
        Execute legal search via CourtListener v4 API."""
        if not self.api_key:
            return "Error: CourtListener API key not configured"
        
        try:
            response = requests.get(
                "https://www.courtlistener.com/api/rest/v4/search/",
                params={"q": query, "type": "o"},
                headers={"Authorization": f"Token {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return f"No legal cases found for query: {query}"
            
            formatted = []
            for i, result in enumerate(results[:5], 1):
                case_name = result.get("caseName", "Unknown")
                court = result.get("court", "Unknown Court")
                date = result.get("dateFiled", "Unknown Date")
                snippet = result.get("snippet", "No summary available")
                
                formatted.append(
                    f"{i}. {case_name}\n"
                    f"   Court: {court}\n"
                    f"   Date: {date}\n"
                    f"   Summary: {snippet}\n"
                )
            
            return "\n".join(formatted)
            
        except requests.Timeout:
            return "Error: CourtListener API request timed out"
        except requests.RequestException as e:
            return f"Error: CourtListener API request failed - {str(e)}"
        except Exception as e:
            return f"Error: Unexpected error during legal search - {str(e)}"


def create_lex_intelligence() -> CrewPipeline:
    """
    Create Lex Intelligence Ultimate pipeline (v3 — optimized).

    Model assignments:
      Agent 1 (Legal Research)      -> GPT-4.1-mini  (tool calling only, 90% cheaper)
      Agent 2 (Statutory)           -> DeepSeek R1   (deep reasoning, best value)
      Agent 3 (Constitutional)      -> DeepSeek R1   (deep reasoning, best value)
      Agent 4 (Contract/Commercial) -> Grok 4.1 Fast (fast, 2M context)
      Agent 5 (Litigation Strategy) -> Gemini 3 Flash (fast strategy synthesis)
      Agent 6 (Synthesis/Drafting)  -> Claude Sonnet 4.6 (best structured synthesis)

    Token optimizations:
      - Tasks 2-4 context=[task1] — only receive case law, not each other
      - Task 5 context=[task1-4] — full picture for strategy
      - Task 6 context=[task1-5] — everything for final synthesis
      - max_tokens caps on all LLMs to prevent runaway generation
    """
    # --- LLM Configuration (v3 — optimized) ---
    # Agent 1: GPT-4.1-mini for tool-based search (90% cheaper than GPT-5.2, equally good at API calls)
    gpt_search_llm = LLM(model="gpt-4.1-mini", api_key=settings.openai_api_key or "dummy", temperature=0.3, max_tokens=2000)
    # Agents 2-3: DeepSeek R1 for deep legal reasoning (best value for chain-of-thought)
    deepseek_llm = LLM(model="deepseek/deepseek-reasoner", api_key=settings.deepseek_api_key or "dummy", temperature=0.3, max_tokens=3000, use_native=False)
    # Agent 4: Grok 4.1 Fast for commercial law (fast, cheap, 2M context)
    grok_llm = LLM(model="xai/grok-4-1-fast", api_key=settings.xai_api_key or "dummy", max_tokens=2000, use_native=False)
    # Agent 5: Gemini 3 Flash for strategy (fast, 1M context)
    gemini_llm = LLM(model="gemini/gemini-3-flash-preview", api_key=settings.google_api_key or "dummy", temperature=0.3, max_tokens=3000, use_native=False)
    # Agent 6: Claude Sonnet 4.6 for synthesis (best at structured writing + large context)
    claude_llm = LLM(model="anthropic/claude-sonnet-4-6", api_key=settings.anthropic_api_key or "dummy", temperature=0.2, max_tokens=4000, use_native=False)
    
    # Initialize legal search tool
    legal_search = LegalSearchTool(api_key=settings.courtlistener_api_key)
    
    # --- Agent Definitions ---
    
    # Agent 1: Legal Research Specialist (GPT-4.1-mini — tool calling only, no deep reasoning needed)
    legal_researcher = Agent(
        role="Legal Research Specialist",
        goal="Find relevant case law, statutes, and legal precedents",
        backstory=(
            "You are an expert legal researcher with 20 years of experience in case law analysis. "
            "You meticulously search through legal databases to find the most relevant precedents. "
            "You always cite specific case names, court jurisdictions, and dates. "
            "You never fabricate case citations or legal references."
        ),
        llm=gpt_search_llm,
        tools=[legal_search],
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 2: Statutory Analyst (DeepSeek R1)
    statutory_analyst = Agent(
        role="Statutory Analyst",
        goal="Analyze statutes, regulations, and legislative intent",
        backstory=(
            "You are a statutory interpretation expert with deep knowledge of legislative drafting. "
            "You analyze statutes in their full context, considering legislative history and purpose. "
            "You always reference specific statute sections and regulatory citations. "
            "You never invent statutory provisions or regulatory text."
        ),
        llm=deepseek_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 3: Constitutional Law Expert (DeepSeek R1)
    constitutional_expert = Agent(
        role="Constitutional Law Expert",
        goal="Evaluate constitutional implications and civil rights issues",
        backstory=(
            "You are a constitutional scholar specializing in fundamental rights and governmental powers. "
            "You analyze issues through the lens of constitutional principles and Supreme Court precedent. "
            "You always ground your analysis in specific constitutional provisions and landmark cases. "
            "You never fabricate Supreme Court opinions or constitutional interpretations."
        ),
        llm=deepseek_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 4: Contract & Commercial Law Specialist (Grok 3 Mini)
    contract_specialist = Agent(
        role="Contract & Commercial Law Specialist",
        goal="Analyze contracts, business transactions, and commercial disputes",
        backstory=(
            "You are a commercial law expert with extensive experience in contract interpretation. "
            "You analyze agreements using principles of contract law and UCC provisions. "
            "You identify key terms, ambiguities, and enforcement issues with precision. "
            "You never invent contract terms or commercial law principles."
        ),
        llm=grok_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 5: Litigation Strategy Advisor (Gemini 2.5 Flash)
    litigation_advisor = Agent(
        role="Litigation Strategy Advisor",
        goal="Develop litigation strategies and assess case strengths",
        backstory=(
            "You are a seasoned litigator with 30 years of courtroom experience. "
            "You evaluate legal positions, anticipate opposing arguments, and assess risks. "
            "You provide practical strategic advice grounded in procedural and evidentiary rules. "
            "You never guarantee outcomes or fabricate litigation statistics."
        ),
        llm=gemini_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 6: Legal Synthesis & Opinion Drafter (Claude)
    synthesis_drafter = Agent(
        role="Master Synthesizer - Legal Opinion Drafter",
        goal="Synthesize all research and source documents into comprehensive legal opinions",
        backstory=(
            "You are the Master Synthesizer with access to all outputs from the specialist agents and raw source documents. "
            "You process vast amounts of information to produce higher-quality long-form legal opinions. "
            "You integrate research from all prior agents with full document context, ensuring nothing is missed. "
            "You write in formal legal style with proper citations and logical organization. "
            "You leverage your large context window to maintain coherence across all sources."
        ),
        llm=claude_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # --- Task Definitions ---
    
    task1 = Task(
        description=(
            "Conduct comprehensive legal research on the user's query. "
            "Search for relevant case law, precedents, and judicial opinions using the legal_search tool. "
            "Focus on finding the most authoritative and recent precedents. "
            "Provide specific case citations with court, year, and holding."
        ),
        expected_output=(
            "A detailed research memo listing 3-5 relevant cases with full citations, "
            "brief summaries of holdings, and explanation of their relevance to the query."
        ),
        agent=legal_researcher
    )
    
    # Tasks 2-4 only receive Task 1 as context (not each other's output)
    # This prevents token bloat where each agent re-ingests all prior outputs
    task2 = Task(
        description=(
            "Analyze applicable statutes and regulations related to the legal issue. "
            "Identify relevant statutory provisions, their text, and legislative intent. "
            "Consider how statutes interact with the case law found in the research."
        ),
        expected_output=(
            "A concise statutory analysis memo identifying applicable statutes with section numbers, "
            "relevant quoted provisions, and explanation of how they apply to the query. "
            "Keep under 800 words to preserve token budget for synthesis."
        ),
        agent=statutory_analyst,
        context=[task1],  # Only receives case law research, not all prior outputs
    )

    task3 = Task(
        description=(
            "Evaluate any constitutional law implications of the legal issue. "
            "Consider fundamental rights, due process, equal protection, and other constitutional principles. "
            "Reference relevant Supreme Court precedents and constitutional provisions."
        ),
        expected_output=(
            "A concise constitutional analysis addressing any constitutional issues raised by the query, "
            "with citations to specific constitutional provisions and Supreme Court cases. "
            "Keep under 800 words to preserve token budget for synthesis."
        ),
        agent=constitutional_expert,
        context=[task1],  # Only receives case law research
    )

    task4 = Task(
        description=(
            "If the query involves contracts or commercial transactions, analyze the legal issues. "
            "Identify key contract terms, potential ambiguities, and commercial law principles. "
            "If not applicable, state that briefly in 1-2 sentences and move on."
        ),
        expected_output=(
            "Either (a) a concise commercial law analysis addressing contract interpretation, enforceability, "
            "and UCC provisions (under 600 words), or (b) a brief statement that commercial law is not applicable."
        ),
        agent=contract_specialist,
        context=[task1],  # Only receives case law research
    )

    # Task 5 receives Tasks 1-4 for strategic assessment
    task5 = Task(
        description=(
            "Based on all prior research, assess the strength of legal positions available. "
            "Identify potential arguments, counterarguments, and litigation risks. "
            "Provide strategic recommendations for proceeding."
        ),
        expected_output=(
            "A litigation strategy memo evaluating the strength of claims, "
            "potential defenses, procedural considerations, and recommended next steps. "
            "Keep under 800 words."
        ),
        agent=litigation_advisor,
        context=[task1, task2, task3, task4],  # Full research context for strategy
    )

    # Task 6 receives ALL tasks for comprehensive synthesis
    task6 = Task(
        description=(
            "As the Master Synthesizer, process all outputs from the specialist agents. "
            "Synthesize all research into a comprehensive legal opinion. "
            "Organize the opinion with: (1) Issue Statement, (2) Brief Answer, "
            "(3) Applicable Law, (4) Analysis, (5) Conclusion. "
            "Use formal legal writing style with proper citations. "
            "Include insights from all prior research."
        ),
        expected_output=(
            "A complete legal opinion memorandum of 1000-2000 words with proper structure, "
            "citations to all sources, and a clear conclusion addressing the user's query."
        ),
        agent=synthesis_drafter,
        context=[task1, task2, task3, task4, task5],  # All prior research
    )
    
    return CrewPipeline(
        name="Lex Intelligence Ultimate",
        description="7-agent legal research and opinion drafting pipeline with Scout synthesizer",
        agents=[
            legal_researcher,
            statutory_analyst,
            constitutional_expert,
            contract_specialist,
            litigation_advisor,
            synthesis_drafter
        ],
        tasks=[task1, task2, task3, task4, task5, task6],
        verbose=True,
        category="intelligence_core",
    )
