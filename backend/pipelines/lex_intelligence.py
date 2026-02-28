"""Lex Intelligence Ultimate - 7-agent legal research pipeline.

Architecture:
  Agent 1 (Legal Research Specialist) -> GPT-4o   : Case law and precedents
  Agent 2 (Statutory Analyst)         -> GPT-4o   : Statutes and regulations  
  Agent 3 (Constitutional Expert)     -> GPT-4o   : Constitutional analysis
  Agent 4 (Contract Specialist)       -> Grok     : Contract interpretation
  Agent 5 (Litigation Advisor)        -> Gemini   : Strategy and risk assessment
  Agent 6 (Master Synthesizer)        -> Scout    : Final opinion with all outputs + raw documents

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
    Create Lex Intelligence Ultimate pipeline.
    
    Model assignments:
      Agent 1 (Legal Research)      -> GPT-4o  (has tools; Anthropic incompatible with CrewAI tool_use)
      Agent 2 (Statutory)           -> GPT-4o
      Agent 3 (Constitutional)      -> GPT-4o  (Anthropic tool_use history conflict in sequential crew)
      Agent 4 (Contract/Commercial) -> Grok 3 Mini Beta via xAI
      Agent 5 (Litigation Strategy) -> Gemini 2.5 Flash via LiteLLM (use_native=False)
      Agent 6 (Synthesis/Drafting)  -> GPT-4o
    """
    # --- LLM Configuration (v2.2) — 5-provider diversity ---
    gpt_llm = LLM(model="gpt-5.2", api_key=settings.openai_api_key or "dummy", temperature=0.4)
    deepseek_llm = LLM(model="deepseek/deepseek-reasoner", api_key=settings.deepseek_api_key or "dummy", temperature=0.3, use_native=False)
    grok_llm = LLM(model="xai/grok-4-1-fast", api_key=settings.xai_api_key or "dummy", use_native=False)
    gemini_llm = LLM(model="gemini/gemini-3-flash-preview", api_key=settings.google_api_key or "dummy", temperature=0.3, use_native=False)
    claude_llm = LLM(model="anthropic/claude-sonnet-4-5-20250929", api_key=settings.anthropic_api_key or "dummy", temperature=0.2, use_native=False)
    
    # Initialize legal search tool
    legal_search = LegalSearchTool(api_key=settings.courtlistener_api_key)
    
    # --- Agent Definitions ---
    
    # Agent 1: Legal Research Specialist (GPT-4o - needs tool calling)
    legal_researcher = Agent(
        role="Legal Research Specialist",
        goal="Find relevant case law, statutes, and legal precedents",
        backstory=(
            "You are an expert legal researcher with 20 years of experience in case law analysis. "
            "You meticulously search through legal databases to find the most relevant precedents. "
            "You always cite specific case names, court jurisdictions, and dates. "
            "You never fabricate case citations or legal references."
        ),
        llm=gpt_llm,
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
    
    task2 = Task(
        description=(
            "Analyze applicable statutes and regulations related to the legal issue. "
            "Identify relevant statutory provisions, their text, and legislative intent. "
            "Consider how statutes interact with the case law found in Task 1."
        ),
        expected_output=(
            "A statutory analysis memo identifying applicable statutes with section numbers, "
            "relevant quoted provisions, and explanation of how they apply to the query."
        ),
        agent=statutory_analyst
    )
    
    task3 = Task(
        description=(
            "Evaluate any constitutional law implications of the legal issue. "
            "Consider fundamental rights, due process, equal protection, and other constitutional principles. "
            "Reference relevant Supreme Court precedents and constitutional provisions."
        ),
        expected_output=(
            "A constitutional analysis addressing any constitutional issues raised by the query, "
            "with citations to specific constitutional provisions and Supreme Court cases."
        ),
        agent=constitutional_expert
    )
    
    task4 = Task(
        description=(
            "If the query involves contracts or commercial transactions, analyze the legal issues. "
            "Identify key contract terms, potential ambiguities, and commercial law principles. "
            "If not applicable, state that and briefly explain why."
        ),
        expected_output=(
            "Either (a) a commercial law analysis addressing contract interpretation, enforceability, "
            "and UCC provisions, or (b) a brief statement that commercial law is not applicable."
        ),
        agent=contract_specialist
    )
    
    task5 = Task(
        description=(
            "Based on all prior research, assess the strength of legal positions available. "
            "Identify potential arguments, counterarguments, and litigation risks. "
            "Provide strategic recommendations for proceeding."
        ),
        expected_output=(
            "A litigation strategy memo evaluating the strength of claims, "
            "potential defenses, procedural considerations, and recommended next steps."
        ),
        agent=litigation_advisor
    )
    
    task6 = Task(
        description=(
            "As Scout, the Master Synthesizer, process all outputs from Tasks 1-5 plus any raw source documents provided. "
            "Synthesize all research from the smaller models into a comprehensive legal opinion. "
            "Leverage your massive context window to ensure nothing is missed from the source materials. "
            "Organize the opinion with: (1) Issue Statement, (2) Brief Answer, "
            "(3) Applicable Law, (4) Analysis, (5) Conclusion. "
            "Use formal legal writing style with proper citations. "
            "Include insights from all prior research and maintain full document context."
        ),
        expected_output=(
            "A complete legal opinion memorandum of 1000-2000 words with proper structure, "
            "citations to all sources, and a clear conclusion addressing the user's query. "
            "Demonstrate higher quality through comprehensive synthesis of all inputs."
        ),
        agent=synthesis_drafter
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
        verbose=True
    )
