"""Lex Intelligence Ultimate - 6-agent legal research pipeline."""

import os
import requests
from typing import Optional
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
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
        Execute legal search.
        
        Args:
            query: Search query
        
        Returns:
            Search results as formatted string
        """
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
            
            # Format results
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
    
    Returns:
        CrewPipeline instance with 6 agents
    """
    # Initialize LLMs
    # Gemini via CrewAI native LLM (bypasses langchain models/ prefix issue)
    grok_llm = ChatOpenAI(
        model="xai/grok-3-mini-beta",  # Using available model instead
        api_key=settings.xai_api_key or "dummy",
        base_url="https://api.x.ai/v1",
    )
    
    # Gemini via CrewAI native LLM (bypasses langchain models/ prefix issue)
    claude_llm = ChatAnthropic(
        model="gpt-4o",  # Using latest available
        api_key=settings.anthropic_api_key or "dummy",
        temperature=0.2
    )
    
    # Gemini via CrewAI native LLM (bypasses langchain models/ prefix issue)
    gpt_llm = ChatOpenAI(
        model="gpt-4o",  # Using available model instead
        api_key=settings.openai_api_key or "dummy",
        temperature=0.4
    )
    
    # Gemini via CrewAI native LLM (bypasses langchain models/ prefix issue)
    # Gemini temporarily replaced with GPT-4o (CrewAI requires crewai[google-genai] for any gemini model)
    gemini_llm = gpt_llm  # TODO: restore Gemini after adding crewai[google-genai] to requirements
    
    # Initialize legal search tool
    legal_search = LegalSearchTool(api_key=settings.courtlistener_api_key)
    
    # Agent 1: Legal Research Specialist
    legal_researcher = Agent(
        role="Legal Research Specialist",
        goal="Find relevant case law, statutes, and legal precedents",
        backstory=(
            "You are an expert legal researcher with 20 years of experience in case law analysis. "
            "You meticulously search through legal databases to find the most relevant precedents. "
            "You always cite specific case names, court jurisdictions, and dates. "
            "You never fabricate case citations or legal references."
        ),
        llm=claude_llm,
        tools=[legal_search],
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 2: Statutory Analyst
    statutory_analyst = Agent(
        role="Statutory Analyst",
        goal="Analyze statutes, regulations, and legislative intent",
        backstory=(
            "You are a statutory interpretation expert with deep knowledge of legislative drafting. "
            "You analyze statutes in their full context, considering legislative history and purpose. "
            "You always reference specific statute sections and regulatory citations. "
            "You never invent statutory provisions or regulatory text."
        ),
        llm=gpt_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 3: Constitutional Law Expert
    constitutional_expert = Agent(
        role="Constitutional Law Expert",
        goal="Evaluate constitutional implications and civil rights issues",
        backstory=(
            "You are a constitutional scholar specializing in fundamental rights and governmental powers. "
            "You analyze issues through the lens of constitutional principles and Supreme Court precedent. "
            "You always ground your analysis in specific constitutional provisions and landmark cases. "
            "You never fabricate Supreme Court opinions or constitutional interpretations."
        ),
        llm=claude_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 4: Contract & Commercial Law Specialist
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
    
    # Agent 5: Litigation Strategy Advisor
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
    
    # Agent 6: Legal Synthesis & Opinion Drafter
    synthesis_drafter = Agent(
        role="Legal Synthesis & Opinion Drafter",
        goal="Synthesize research into comprehensive legal opinions",
        backstory=(
            "You are a legal writing expert who transforms complex research into clear opinions. "
            "You integrate multiple legal authorities into coherent, well-structured analyses. "
            "You write in formal legal style with proper citations and logical organization. "
            "You never add sources or arguments not provided by the research team."
        ),
        llm=claude_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Task 1: Legal Research
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
    
    # Task 2: Statutory Analysis
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
    
    # Task 3: Constitutional Review
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
    
    # Task 4: Contract/Commercial Analysis
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
    
    # Task 5: Litigation Strategy
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
    
    # Task 6: Final Opinion
    task6 = Task(
        description=(
            "Synthesize all research from Tasks 1-5 into a comprehensive legal opinion. "
            "Organize the opinion with: (1) Issue Statement, (2) Brief Answer, "
            "(3) Applicable Law, (4) Analysis, (5) Conclusion. "
            "Use formal legal writing style with proper citations. "
            "Only include information from the prior tasks - do not add new sources."
        ),
        expected_output=(
            "A complete legal opinion memorandum of 1000-2000 words with proper structure, "
            "citations to all sources, and a clear conclusion addressing the user's query."
        ),
        agent=synthesis_drafter
    )
    
    # Create pipeline
    return CrewPipeline(
        name="Lex Intelligence Ultimate",
        description="6-agent legal research and opinion drafting pipeline",
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
