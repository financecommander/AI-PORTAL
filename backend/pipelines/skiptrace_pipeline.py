"""Skip Trace Pipeline - Multi-agent contact location and identity verification.

Performs comprehensive skip tracing to locate contact information,
verify identities, and compile background intelligence on subjects.

Agents:
  1. Public Records Researcher - Court records, property, UCC, voter rolls
  2. Digital Footprint Analyst - Social media, business registrations, web presence
  3. Identity Verifier         - Cross-reference data, resolve name conflicts, SSN traces
  4. Skip Trace Reporter       - Consolidated contact dossier with confidence scores
"""

import time
import logging
from typing import Optional, Callable, Any

import requests
from backend.pipelines.base_pipeline import BasePipeline, PipelineResult
from backend.providers.factory import get_provider
from backend.providers.base import ProviderResponse
from backend.config.settings import settings
from backend.tools.skiptrace.tool import run_skiptrace_scraper

logger = logging.getLogger(__name__)


def _search_court_records(person_name: str) -> str:
    """Query CourtListener v4 API for court records matching a person's name.

    Returns formatted results or an error/empty message. Gracefully degrades
    if the API key is missing or the request fails.
    """
    api_key = settings.courtlistener_api_key
    if not api_key:
        return "[CourtListener] API key not configured — skipping live court search."

    try:
        response = requests.get(
            "https://www.courtlistener.com/api/rest/v4/search/",
            params={"q": person_name, "type": "r"},  # "r" = RECAP (docket) search
            headers={"Authorization": f"Token {api_key}"},
            timeout=12,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            return f"[CourtListener] No court records found for: {person_name}"

        formatted = [f"[CourtListener] {len(results)} result(s) for '{person_name}':\n"]
        for i, r in enumerate(results[:8], 1):
            case_name = r.get("caseName", r.get("case_name", "Unknown"))
            court = r.get("court", r.get("court_id", "Unknown Court"))
            date = r.get("dateFiled", r.get("date_filed", "Unknown Date"))
            docket = r.get("docketNumber", r.get("docket_number", ""))
            snippet = r.get("snippet", "")
            formatted.append(
                f"{i}. {case_name}\n"
                f"   Court: {court} | Docket: {docket}\n"
                f"   Filed: {date}\n"
                f"   {snippet[:200]}\n"
            )
        return "\n".join(formatted)

    except requests.Timeout:
        return "[CourtListener] Request timed out."
    except requests.RequestException as e:
        return f"[CourtListener] Request failed: {e}"
    except Exception as e:
        return f"[CourtListener] Unexpected error: {e}"


class SkipTracePipeline(BasePipeline):
    """
    4-agent pipeline for skip tracing and contact location.

    Agents:
      1. Public Records Researcher - Court, property, UCC, voter records
      2. Digital Footprint Analyst - Online presence, social, business filings
      3. Identity Verifier         - Cross-reference and resolve identity
      4. Skip Trace Reporter       - Final dossier with confidence scores
    """

    AGENT_NAMES = [
        "Public Records Researcher",
        "Digital Footprint Analyst",
        "Identity Verifier",
        "Skip Trace Reporter",
    ]

    def __init__(self):
        super().__init__(
            name="Skip Trace Engine",
            description=(
                "Multi-agent skip tracing pipeline for locating contact information, "
                "verifying identities, and compiling background intelligence"
            ),
        )

    def get_agents(self) -> list[dict[str, Any]]:
        return [
            {"name": "Public Records Researcher", "goal": "Search public records for addresses, phone numbers, property, and court records", "model": "gemini-2.5-flash"},
            {"name": "Digital Footprint Analyst", "goal": "Map online presence, social media, business registrations, and web activity", "model": "gemini-2.5-flash"},
            {"name": "Identity Verifier", "goal": "Cross-reference all data sources to verify identity and resolve conflicts", "model": "gemini-2.5-flash"},
            {"name": "Skip Trace Reporter", "goal": "Compile final skip trace dossier with confidence-scored contact information", "model": "gpt-4o"},
        ]

    def estimate_cost(self, input_length: int) -> float:
        return 0.03

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

        # ═══ AGENT 1: Public Records Researcher ══════════════════════
        a1_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Public Records Researcher"})

        public_records_report, a1_tokens = await self._run_public_records_researcher(query)

        a1_ms = (time.perf_counter() - a1_start) * 1000
        agent_breakdown.append({
            "agent": "Public Records Researcher",
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
                "agent": "Public Records Researcher",
                "duration_ms": round(a1_ms, 1),
                "output": public_records_report[:500],
            })

        # ═══ AGENT 2: Digital Footprint Analyst ══════════════════════
        a2_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Digital Footprint Analyst"})

        digital_report, a2_tokens = await self._run_digital_footprint_analyst(query)

        a2_ms = (time.perf_counter() - a2_start) * 1000
        agent_breakdown.append({
            "agent": "Digital Footprint Analyst",
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
                "agent": "Digital Footprint Analyst",
                "duration_ms": round(a2_ms, 1),
                "output": digital_report[:500],
            })

        # ═══ AGENT 3: Identity Verifier ══════════════════════════════
        a3_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Identity Verifier"})

        identity_report, a3_tokens = await self._run_identity_verifier(
            query, public_records_report, digital_report,
        )

        a3_ms = (time.perf_counter() - a3_start) * 1000
        agent_breakdown.append({
            "agent": "Identity Verifier",
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
                "agent": "Identity Verifier",
                "duration_ms": round(a3_ms, 1),
                "output": identity_report[:500],
            })

        # ═══ AGENT 4: Skip Trace Reporter ════════════════════════════
        a4_start = time.perf_counter()
        if on_progress:
            await on_progress("agent_start", {"agent": "Skip Trace Reporter"})

        final_report, a4_tokens = await self._run_skip_trace_reporter(
            query, public_records_report, digital_report, identity_report,
        )

        a4_ms = (time.perf_counter() - a4_start) * 1000
        agent_breakdown.append({
            "agent": "Skip Trace Reporter",
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
                "agent": "Skip Trace Reporter",
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

    @staticmethod
    def _parse_subject(query: str) -> tuple[str, str, str]:
        """Best-effort extraction of (name, state, city) from free-text query."""
        import re
        # Strip command prefixes first
        name_part = query
        for prefix in ("skip trace ", "skip-trace ", "skiptrace ", "find ", "locate "):
            if name_part.lower().startswith(prefix):
                name_part = name_part[len(prefix):]
                break
        # Heuristic: look for "in <State>" or "in <City>, <State>"
        m = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*))?', name_part)
        state = ""
        city = ""
        if m:
            if m.group(2):
                city = m.group(1).strip()
                state = m.group(2).strip()
            else:
                state = m.group(1).strip()
            name_part = name_part[:m.start()].strip().rstrip(',')
        return name_part.strip(), state, city

    async def _run_public_records_researcher(self, query: str) -> tuple[str, dict]:
        """Agent 1: Public records — court, property, UCC, voter rolls.

        Two live data sources before LLM reasoning:
          1. skip-trace-scraper subprocess (web scraping tool)
          2. CourtListener v4 API (federal court records)
        """
        name, state, city = self._parse_subject(query)

        # ── Live scraper ─────────────────────────────────────────────
        scraper_data = run_skiptrace_scraper(name=name, state=state, city=city)
        logger.info("SkipTrace scraper returned %d chars", len(scraper_data))

        # ── Live court records lookup ────────────────────────────────
        court_data = _search_court_records(name if name else query)
        logger.info("CourtListener returned %d chars", len(court_data))

        provider = get_provider("google")

        system_prompt = (
            "You are an expert skip trace investigator specializing in public records research. "
            "Given a person's name and any known details (state, city, DOB, SSN last 4, etc.), "
            "conduct a thorough public records analysis:\n\n"
            "1. **Property Records** - Real estate ownership, deeds, transfers, property tax records\n"
            "2. **Court Records** - Civil/criminal cases, traffic tickets, divorce filings, evictions\n"
            "3. **UCC Filings** - Secured transactions listing the subject as debtor or secured party\n"
            "4. **Voter Registration** - Address, party affiliation, registration date\n"
            "5. **Vehicle Registration** - DMV records if available in the state\n"
            "6. **Known Addresses** - All residential addresses found, sorted by most recent\n"
            "7. **Known Phone Numbers** - Landline and mobile numbers from public directories\n\n"
            "You have been provided with LIVE data from two sources below:\n"
            "  1. SkipTrace Scraper — web-scraped public records\n"
            "  2. CourtListener API — federal court records\n\n"
            "Incorporate ALL real results into your analysis. Clearly cite which source "
            "each finding came from. For categories without live data, reason about what "
            "public records would show and recommend databases to check.\n\n"
            "For each piece of information, note the source and confidence level. "
            "Flag any discrepancies (e.g., multiple addresses in different states)."
        )

        user_content = (
            f"Skip trace subject: {query}\n\n"
            f"── LIVE SCRAPER RESULTS ──\n{scraper_data}\n\n"
            f"── LIVE COURT RECORDS (CourtListener API) ──\n{court_data}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_digital_footprint_analyst(self, query: str) -> tuple[str, dict]:
        """Agent 2: Digital presence — social media, business filings, web."""
        provider = get_provider("google")

        system_prompt = (
            "You are a digital intelligence analyst specializing in online skip tracing. "
            "Given a person's name and known details, map their digital footprint:\n\n"
            "1. **Social Media Profiles** - Facebook, LinkedIn, Instagram, X/Twitter, TikTok, etc.\n"
            "   Note: usernames, profile pictures, location listed, employment listed\n"
            "2. **Business Registrations** - Secretary of State filings, LLC/Corp records, DBAs\n"
            "3. **Professional Licenses** - State licensing boards (real estate, contractor, medical, etc.)\n"
            "4. **Web Presence** - Personal websites, blog posts, press mentions, news articles\n"
            "5. **Email Addresses** - Known emails from public sources, data breach compilations\n"
            "6. **Association Memberships** - Trade organizations, alumni directories, church directories\n"
            "7. **Employment History** - LinkedIn timeline, company websites, press releases\n\n"
            "For each finding, rate confidence as HIGH, MEDIUM, or LOW. "
            "Note any potential name collisions (common names) and how you resolved them. "
            "Describe the search methodology you would use for each source."
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": query}],
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_identity_verifier(
        self, query: str, public_records: str, digital_footprint: str,
    ) -> tuple[str, dict]:
        """Agent 3: Cross-reference data, resolve conflicts, verify identity."""
        provider = get_provider("google")

        system_prompt = (
            "You are an identity verification specialist with expertise in resolving ambiguous "
            "skip trace results. You receive raw findings from public records and digital footprint "
            "analysts and must:\n\n"
            "1. **Cross-Reference** - Match addresses across sources, verify phone→address links\n"
            "2. **Resolve Conflicts** - When sources disagree, assess which is more current/reliable\n"
            "3. **Eliminate False Positives** - Identify records that belong to different people with same name\n"
            "4. **Age/DOB Consistency** - Verify reported ages match across sources\n"
            "5. **Associate Mapping** - Identify known associates, relatives, co-residents\n"
            "6. **Current vs. Historical** - Clearly demarcate current contact info vs. historical\n"
            "7. **Confidence Scoring** - Rate each contact detail: CONFIRMED, LIKELY, POSSIBLE, STALE\n\n"
            "Be rigorous — a wrong phone number or address is worse than no result."
        )

        user_content = (
            f"Skip trace subject:\n{query[:2000]}\n\n"
            f"Public Records Findings:\n{public_records[:3000]}\n\n"
            f"Digital Footprint Findings:\n{digital_footprint[:3000]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=3000,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }

    async def _run_skip_trace_reporter(
        self, query: str, public_records: str,
        digital_footprint: str, identity_verification: str,
    ) -> tuple[str, dict]:
        """Agent 4: Final skip trace dossier with confidence scores."""
        provider = get_provider("openai")

        system_prompt = (
            "You are a senior skip trace investigator compiling a final contact dossier. "
            "Produce a formal Skip Trace Report in Markdown. Structure:\n\n"
            "# Skip Trace Report\n\n"
            "## Subject Summary\n"
            "Full name, known aliases, DOB, last 4 SSN (if available)\n\n"
            "## Current Contact Information\n"
            "| Type | Detail | Confidence | Source |\n"
            "Address, phone, email — only CONFIRMED or LIKELY entries\n\n"
            "## Historical Addresses\n"
            "Timeline of known addresses with date ranges\n\n"
            "## Known Associates & Relatives\n"
            "Names and relationships with contact info if available\n\n"
            "## Employment & Business Interests\n"
            "Current and prior employment, owned businesses, professional licenses\n\n"
            "## Digital Presence\n"
            "Social media handles, websites, email addresses\n\n"
            "## Public Records Summary\n"
            "Property, court records, liens, vehicle registrations\n\n"
            "## Confidence Assessment\n"
            "Overall confidence rating: HIGH / MEDIUM / LOW\n"
            "Key data gaps and recommended next steps\n\n"
            "## Recommended Next Steps\n"
            "Specific actions to locate if current info is insufficient\n\n"
            "Be thorough but concise. Use tables for contact information. "
            "NEVER fabricate contact details — only report what was found."
        )

        user_content = (
            f"Subject:\n{query[:2000]}\n\n"
            f"Public Records:\n{public_records[:2500]}\n\n"
            f"Digital Footprint:\n{digital_footprint[:2500]}\n\n"
            f"Identity Verification:\n{identity_verification[:2500]}"
        )

        response = await provider.send_message(
            messages=[{"role": "user", "content": user_content}],
            model="gpt-4o",
            temperature=0.3,
            max_tokens=4096,
            system_prompt=system_prompt,
        )

        return response.content, {
            "input": response.input_tokens,
            "output": response.output_tokens,
            "cost": response.cost_usd,
        }
