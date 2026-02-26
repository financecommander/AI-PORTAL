# Lex Intelligence v2.2 — Multi-Jurisdictional Expansion Planning Spec

**Status:** Planning (begins after v2.1 stabilization)
**Author:** Sean Grady, CEO / Claude Opus (Architecture) / Grok 4.20 Heavy (Competitive Intel + Review)
**Date:** February 25, 2026 (revised)
**Document:** `docs/LEX_v2.2_PLANNING_SPEC.md`
**Revision:** 3.0 — Adds market context, self-evolving feedback loops, Validator Agent, proactive Watch Agents, Compliance & Risk Agent (EU AI Act self-classification), Guardian Agent (anomaly monitoring), interoperability protocols (MCP/ACP/A2A), domain-specific adapters, weighted explainability, go-to-market strategy, and agentic liability framework.

---

## Executive Summary

Lex Intelligence v2.2 transforms the pipeline from a US-focused, fixed sequential chain into an adaptive, self-improving, multi-jurisdictional legal research engine. The system evolves across three dimensions: **architecture** (dynamic orchestration, parallel execution, feedback loops), **governance** (Guardian Agent, Compliance Agent, liability framework, explainability), and **scope** (EU/GCC jurisdiction branches, proactive monitoring, interoperability with external legal ecosystems).

This spec captures the full v2.0 → v2.1 → v2.2 → v2.3 evolution: model upgrades, intra-pipeline parallelism, divergence detection, human-in-the-loop, CourtListener hybrid, resilience patterns, governance-first agents, self-evolving memory, proactive watch capabilities, interoperability protocols, and a go-to-market path from internal tool to public SaaS.

This spec is informed by competitive analysis of Harvey, Lexis+ Protégé/CoCounsel, LegalOn, Luminance, HAQQ Legal AI, and Usul.ai; a formal architectural review from Grok 4.20 Heavy; and 2026 industry analysis from Thomson Reuters, Gartner, and emerging agentic AI governance frameworks.

---

## Competitive Landscape (February 2026)

### Key Competitors

| Platform | Architecture | Strengths | Gaps We Can Exploit |
|----------|-------------|-----------|-------------------|
| **Harvey** | Single-model, iterative refinement | Deep Westlaw/LexisNexis integration, enterprise clients | Single provider, no transparent cross-validation |
| **CoCounsel (Lexis Protégé)** | 4+ agents, GPT-powered, "Deep Research" | Massive proprietary corpus, Bluebook citations, guided multi-step | GPT-only, no multi-provider peer review |
| **LegalOn** | 5 agentic tools, reusable | Contract review, multilingual, cross-jurisdiction | Narrow focus (contracts), not full legal research |
| **Luminance** | Proprietary AI | M&A due diligence, 80+ languages | Enterprise-only pricing, not developer-accessible |
| **HAQQ Legal AI** | Jurisdiction-aware chat | US/UK/EU/UAE/Saudi/Egypt/Lebanon coverage | Limited depth per jurisdiction |
| **Usul.ai** | Sharia-specialized | 8,000+ Islamic legal texts, deep Sharia coverage | Narrow scope, no multi-jurisdiction synthesis |
| **Lex Intelligence (ours)** | 6 agents, 4 LLMs, cross-validated | Multi-provider peer review, transparent cost/confidence | US-only, fixed chain, no dynamic routing |

### Our Structural Advantage

Harvey, CoCounsel, and LegalOn run on single LLM providers. Our multi-provider architecture (Anthropic + OpenAI + xAI + Google) provides built-in cross-validation that no single-provider platform can replicate. The v2.2 expansion leverages this architecture for multi-jurisdictional analysis — each jurisdiction branch can use the optimal provider for that legal system.

No exact peer offers a 6-agent, 4-provider, fintech-specific chain with public API grounding. CoCounsel and Lexis Protégé are the closest in agentic depth, but they prioritize proprietary silos over open diversity. Our transparency in cost/confidence per agent is unique in the market.

### Grok 4.20 External Review Score

Grok 4.20 Heavy rated the current v2.0 pipeline at **8.5/10**, noting it as "one of the more thoughtful and realistic multi-agent setups" in the 2026 landscape. With model upgrades and the improvements in this spec, projected rating: **9.5+/10**.

### Market Context (February 2026)

The legal AI space is shifting decisively toward agentic and multi-agent systems, but adoption is still early — creating a narrow window for well-architected entrants.

| Metric | Value | Source |
|--------|-------|--------|
| Law firms/legal depts using agentic AI | 15-18% | Thomson Reuters 2026 Report |
| Enterprise software with agentic capabilities by 2028 | 33% | Gartner |
| Agentic AI projects expected to fail | 40%+ | Gartner (costs, unclear ROI, weak governance) |
| Guardian agent market share by 2030 | 10-15% of agentic market | Gartner |

The 40%+ failure rate is our opening: most failures stem from weak governance, unclear ROI, and cost overruns — exactly the problems we address with transparent per-agent cost tracking, confidence scoring, human-in-the-loop, and the Guardian/Compliance agents introduced in this spec. Our position as a governance-first, cost-transparent, multi-provider pipeline targets the gap that will kill 40% of competitors.

---

## Phase 0: Model Upgrade Path (v2.0.1 → v2.1)

Before v2.2 architecture changes, the existing 6-agent pipeline needs model refreshes. As of February 25, 2026, several model strings are 3-9 months behind frontier.

### Immediate Upgrades (v2.0.1 — No Architecture Changes)

| Agent | Current Model | Upgrade Target | Rationale | Cost Impact |
|-------|--------------|----------------|-----------|-------------|
| 1, 3, 6 | `claude-opus-4-20250514` | `claude-opus-4-6` | Opus 4.6 (Feb 5, 2026): 1M context beta, better agentic planning, reduced long-chain errors, top on GDPval-AA + BrowseComp | Pricing stable (~$5/$25 per M tokens) |
| 2 | `gpt-4o` | `claude-sonnet-4-5-20250929` or `gpt-5.2` | Sonnet 4.5 near-Opus at ~60% cost; GPT-5.x better reasoning but higher cost | Sonnet: ~$3/$15. GPT-5.x: higher. Evaluate both. |
| 4 | `grok-beta` | `grok-4-20` (when API GA) | Built-in 4-agent peer review, reduced hallucination (12% → 4.2%), real-time X data | Moderate increase due to internal agent overhead |
| 5 | `gemini-2.0-flash-exp` | `gemini-3.1-pro` or latest Flash stable | Gemini 3.1 Pro (Feb 19): ARC-AGI-2 leader, massive reasoning jump, strong counterargument generation | ~$2-$4.50 per M input |

### Cost Estimate Correction

Grok's review flagged our $0.77/run estimate as optimistic. Realistic range with current pricing and verbose outputs:

| Scenario | Current Estimate | Corrected Range |
|----------|-----------------|-----------------|
| Simple US query | $0.30 | $0.30 - $0.50 |
| Typical US query | $0.77 | $0.80 - $1.20 |
| Complex multi-agent | $0.77 | $1.00 - $1.50 |

All cost projections in this spec use **ranges, not point estimates**, to reflect real-world variance.

---

## Phase 1: Intra-Pipeline Parallelism (v2.1)

### Problem

The current fully sequential chain (Agent 1 → 2 → 3 → 4 → 5 → 6) creates unnecessary wait time. Agents 2 (Statutory), 3 (Constitutional), and 4 (Contract) are largely independent once case law is established — they all reference Agent 1's output but don't depend on each other.

### Proposed Architecture

```
Agent 1 (Legal Research, Claude Opus 4.6)
    │
    │  CourtListener grounding — must complete first
    │
    ├──────────────┬──────────────┐
    │              │              │
    ▼              ▼              ▼
Agent 2         Agent 3        Agent 4
(Statutory)     (Const'l)      (Contract)
(Sonnet 4.5)    (Opus 4.6)     (Grok 4.20)
    │              │              │
    └──────────────┼──────────────┘
                   │
                   ▼
            ┌─────────────┐
            │ Merge Node  │
            │ (aggregate)  │
            └──────┬──────┘
                   │
                   ▼
            Agent 5 (Litigation Strategy, Gemini 3.1 Pro)
                   │
                   ▼
            Agent 6 (Synthesis, Claude Opus 4.6)
```

### Implementation Notes

CrewAI supports parallel execution via task dependencies and conditional routing (`@router` decorators, `or_`/`and_` operators for branching). Define Agent 2, 3, 4 tasks with dependency only on Agent 1 completion and no inter-branch dependencies.

The merge node is a lightweight aggregator (not a full LLM call) that collects parallel outputs and concatenates them as context for Agent 5.

### Expected Impact

- Speed: 40-60 second reduction (parallel branches run concurrently; LLM inference is the bottleneck)
- Cost: Negligible (same calls, just overlapped in time)
- Duration target: 20-80 seconds (down from 30-120)

### Divergence Check at Merge

Add a lightweight divergence check in the merge node before passing to Agent 5:

- If branch outputs contradict Agent 1 facts → flag for retry or lower confidence
- If branches produce opposing conclusions → annotate for Agent 5 and 6

---

## Phase 2: Divergence Detection & Voting (v2.1)

### Problem

Currently, Agent 6 (Synthesis) receives all prior output and must silently reconcile conflicts. If Agents 2-5 disagree fundamentally (e.g., statutory analysis says favorable but constitutional analysis says unfavorable), this should be explicitly surfaced, not buried.

### Approach: Embedding-Based Divergence Scoring

After parallel branches complete, before synthesis:

1. Each agent outputs an explicit 1-2 sentence **position summary** (add to backstory prompt: "End your analysis with a one-sentence Position Summary stating your overall conclusion.")

2. Embed position summaries using a cheap embedding model (OpenAI `text-embedding-3-small` or HuggingFace sentence-transformers)

3. Compute pairwise cosine similarities

4. If average similarity < threshold (0.65-0.75), trigger divergence alert

### Voting Mechanism

A lightweight judge (Gemini Flash, ~$0.001 per call) scores agreement on three dimensions:
- **Conclusion polarity**: favorable / unfavorable / neutral
- **Confidence level**: high / medium / low
- **Primary risk identified**: text summary

Pass aggregated vote to Agent 6 synthesis prompt: "Divergence detected: 4/5 agents lean favorable; Agent 3 dissents on constitutional grounds. Weigh constitutional analysis carefully."

### Integration Point

Insert between merge node and Agent 5:

```
Merge Node → Divergence Scorer → Agent 5 (with divergence context) → Agent 6 (with vote summary)
```

Cost: ~$0.002-$0.01 per run (embedding + Flash judge). Negligible.

### Relationship to v2.2 Convergence Checker

The v2.1 Divergence Scorer handles **intra-pipeline** disagreement (within the US chain). The v2.2 Convergence Checker (Agent IC1, Gemini 3.1 Pro) handles **inter-jurisdictional** conflicts (US vs EU vs GCC). They are complementary — in v2.2, both run: divergence scoring within each branch, convergence checking across branches.

---

## Phase 3: Human-in-the-Loop System (v2.1)

### Rationale

Even with 6-layer hallucination defenses, legal opinions in fintech (constitutional tender, lending regs) can have massive downstream risk. Periodic human review catches subtle errors that automated checks miss.

### Auto-Flagging Rules

A pipeline run is flagged for human review if ANY of:

| Trigger | Condition |
|---------|-----------|
| **Keyword** | Query contains "constitutional", "legal tender", "Article I Section 10", "preemption", "class action", or monetary value > $1M |
| **Divergence** | Divergence score (Phase 2) exceeds threshold |
| **Low confidence** | Agent 6 outputs Confidence = MEDIUM or LOW |
| **Random sampling** | 5-10% of all runs (configurable) |

### Review Workflow

```
Pipeline completes
    │
    ├── Not flagged → Deliver immediately to user
    │
    └── Flagged → Route to review queue
                    │
                    ▼
              ┌─────────────┐
              │ Review Queue │
              │ (Slack +     │
              │  Dashboard)  │
              └──────┬──────┘
                     │
                     ▼
              Human Reviewer sees:
              - Original query
              - Full agent trace (per-agent output, tokens, cost)
              - Divergence score
              - Confidence ratings
                     │
                     ├── Approve → Release to user
                     ├── Request retry → Re-run pipeline with adjusted params
                     └── Annotate corrections → Feed back as prompt improvements
```

### WebSocket Integration

New event type for flagged runs:

```json
{ "type": "human_review_pending", "data": { "reason": "low_confidence", "eta_hours": "1-4" } }
```

Frontend displays: "This opinion has been flagged for expert review — estimated delivery: 1-4 hours."

### Review Frequency

Start at 5-10% random + all auto-flags. Adjust based on error rate from reviews. Target: <2% of reviewed opinions require corrections.

---

## Phase 4: CourtListener Monitoring & Bulk Hybrid (v2.1)

### Problem

CourtListener API allows 5,000 queries/hour for authenticated users. Agent 1 typically makes 3-10 searches per pipeline run. At scale (e.g., 100+ runs/day for 10 team members in v2.1), we risk rate-limiting without monitoring.

### Usage Monitoring

#### Minimal Version (FastAPI endpoint)

```python
# courtlistener_monitor.py — singleton, thread-safe
class CourtListenerMonitor:
    HOURLY_CAP = 5000
    ALERT_THRESHOLD = 0.70  # 3,500 calls

    def record_call(self) -> tuple[int, int]:
        # Track hourly (deque) + daily total
        # Alert via Slack if > threshold
        ...

    def get_stats(self) -> dict:
        # Returns {"hourly_usage": N, "hourly_cap": 5000, "daily_total": N}
        ...
```

Expose at `GET /api/v2/monitoring/courtlistener` for frontend dashboard gauge.

#### Scalable Version (Prometheus + Grafana)

```python
from prometheus_client import Counter, Gauge
cl_calls_total = Counter('courtlistener_api_calls_total', 'Total CourtListener API calls')
cl_hourly_usage = Gauge('courtlistener_hourly_usage', 'Current hourly calls')
```

Grafana dashboard: time-series panel for hourly usage, alert rule if >3,500 for 5 minutes, historical trends.

### Bulk Hybrid Lookup

#### Strategy

Use quarterly S3 bulk snapshots for historical depth + real-time API for fresh opinions.

| Source | Use Case | Rate Limit | Cost |
|--------|----------|------------|------|
| Bulk DB (local) | Historical federal constitutional cases | None | Storage only |
| API (live) | Recent opinions, fresh filings | 5,000/hr | Free |
| Redis cache | Recent API results (TTL 24h) | None | Memory |

#### Implementation

1. **Quarterly download** (cron): Pull opinion snapshots from `s3://com-courtlistener-storage/bulk-data/`

2. **Filter to relevant subset**: Federal appellate + SCOTUS cases mentioning Constitution, Article I, Section 10, Tender, Monetary, Commerce Clause, UCC. Estimated size: 1-5 GB (vs. 50+ GB full corpus)

3. **Index in PostgreSQL** with full-text search (GIN index on opinion_text) or pgvector for semantic search

4. **Hybrid lookup in Agent 1**:
   - First: Search local bulk DB (fast, no rate limit)
   - If results < 3 relevant OR query mentions recent year: Fall back to live API
   - Combine: Deduplicate by case ID, prioritize API-fresh data
   - Cache recent API results in Redis (TTL 24h)

5. **Stale data alert**: If bulk snapshot > 3 months old, alert: "Bulk data stale — potential gap in historical precedents"

#### Free Law Project Contact

For production scale, contact `data-consulting@free.law` for:
- Custom bulk extracts (pre-filtered federal constitutional)
- Higher API quota negotiation
- Bulk data agreement (non-profits/companies get reasonable deals, $140-$750/hr for consulting)

---

## Phase 5: Resilience Patterns (v2.1)

### Problem

Grok's review flagged: no retry logic, no fallback if a provider is down, no timeout handling. A production legal pipeline cannot silently fail.

### Per-Agent Timeout

| Agent | Max Timeout | Rationale |
|-------|-------------|-----------|
| Agent 1 (Research + API) | 45s | CourtListener latency + LLM |
| Agents 2-4 (parallel) | 30s each | LLM-only, no external calls |
| Agent 5 (Strategy) | 30s | LLM-only |
| Agent 6 (Synthesis) | 60s | Largest input context |

If timeout exceeded: Cancel agent, insert "Agent N timed out — analysis unavailable for this section" into pipeline context, continue to next agent. Flag for human review.

### Retry Logic

```
Attempt 1 → fail (timeout or 5xx) → wait 2s → Attempt 2 → fail → wait 4s → Attempt 3 → fail → mark agent as failed
```

Max 3 retries per agent. Exponential backoff (2s, 4s, 8s).

### Provider Fallback Matrix

| Primary Provider | Fallback Provider | Fallback Model |
|-----------------|-------------------|----------------|
| Anthropic (Agents 1, 3, 6) | OpenAI | GPT-5.x (or GPT-4o) |
| OpenAI / Sonnet (Agent 2) | Anthropic | Claude Haiku 4.5 |
| xAI Grok (Agent 4) | Google | Gemini 3.1 Pro |
| Google Gemini (Agent 5) | xAI | Grok 4.20 |

Fallback activates after 3 failed retries on primary. Log: "Agent N failed over to {fallback_model}." Include in pipeline trace.

### CourtListener Fallback

If CourtListener returns 429 (rate limited) or 5xx:
1. Check bulk DB for cached results
2. If bulk insufficient: Proceed without external grounding, but flag confidence as LOW and trigger human review
3. Never fabricate citations — degrade gracefully

---

## Phase 5.5: Self-Evolving Feedback Loops (v2.1 → v2.2)

### Problem

The current pipeline treats every run as stateless — it learns nothing from past queries. When divergence is detected and resolved (either by Agent 6 synthesis or human review), that resolution is lost. The same divergence pattern may recur and be resolved differently next time.

### Architecture: Run Memory Store

After each pipeline run, store a structured record:

```json
{
  "run_id": "uuid",
  "query_hash": "sha256",
  "query_category": "constitutional_tender",
  "divergence_detected": true,
  "divergence_pattern": "statutory_favorable_vs_constitutional_unfavorable",
  "resolution": "constitutional_analysis_prevailed",
  "human_reviewed": true,
  "human_correction": null,
  "agent_weights_applied": { "agent_1": 0.20, "agent_3": 0.45, "agent_5": 0.15 },
  "confidence_final": "HIGH",
  "timestamp": "2026-04-15T14:30:00Z"
}
```

### Feedback Loop Mechanics

1. **Divergence Resolution Memory**: When the same divergence pattern recurs (e.g., statutory vs. constitutional tension on tender law), bias synthesis toward the previously validated resolution. Weight: 0.1 initial, increasing to 0.3 after 5+ consistent human-validated resolutions.

2. **Agent Accuracy Tracking**: Track per-agent accuracy over time. If Agent 4 (Contract/Grok) consistently produces conclusions that Agent 6 overrides or humans correct, reduce its synthesis weight. If Agent 3 (Constitutional/Opus) consistently anchors final conclusions, increase its weight.

3. **Query Category Learning**: Classify queries into categories (constitutional tender, lending compliance, UCC disputes, cross-border fintech). Over time, the Orchestrator learns which agent configurations perform best for each category and adjusts routing.

4. **Prompt Evolution**: After N human corrections on a specific pattern, auto-suggest backstory prompt refinements for the relevant agent. Human approves before deployment.

### Storage

PostgreSQL table `pipeline_run_memory` with indexes on `query_category`, `divergence_pattern`, and `timestamp`. Retained for 12 months, then archived.

### Privacy

Run memory stores query hashes and patterns, not raw query text. User-identifiable data is excluded. Memory is scoped to the organization (Calculus Holdings entities), not shared across tenants in future SaaS.

---

## Phase 5.6: Validator Agent — Ground Truth Checking (v2.2)

### Problem

The divergence scorer (Phase 2) compares agents to each other — it detects disagreement but cannot determine who is correct. A Validator Agent compares agent output against known ground truth.

### Agent Specification

| Parameter | Value |
|-----------|-------|
| **Role** | Ground Truth Validator |
| **LLM** | Gemini 3.1 Pro (structured reasoning, fast) |
| **Temperature** | 0.1 |
| **Tools** | CourtListener bulk DB (local), EUR-Lex API, case citation verifier |
| **Timeout** | 20s |
| **Runs** | Parallel to pipeline (does NOT block execution) |
| **Purpose** | Verify citations, case names, statute numbers, and key factual claims against known-correct sources |

### Validation Checks

1. **Citation verification**: Every case citation (name, court, year) checked against CourtListener bulk DB or live API
2. **Statute verification**: Every statute reference (section number, title) checked against known statutory databases
3. **Factual claim spot-check**: Key factual claims (e.g., "Article I Section 10 prohibits states from...") verified against constitutional text
4. **Fabrication detection**: Flag any citation that returns zero matches — potential hallucination

### Output

```json
{
  "citations_checked": 12,
  "citations_verified": 11,
  "citations_unverifiable": 1,
  "citations_fabricated": 0,
  "statutes_checked": 5,
  "statutes_verified": 5,
  "factual_claims_checked": 3,
  "factual_claims_verified": 3,
  "overall_validity": "HIGH",
  "flags": ["Citation 'Smith v. Jones (2024)' not found in CourtListener — verify manually"]
}
```

### Relationship to Other Agents

- Divergence Scorer: Compares agents to each other (agreement)
- Validator: Compares agents to ground truth (accuracy)
- Guardian: Monitors pipeline health (anomalies)
- Human-in-the-loop: Final authority (judgment)

---

## Phase 6: Architecture — Adaptive Orchestrated Pipeline (v2.2)

### Current (v2.0): Fixed Sequential Chain

```
Query → Agent 1 → Agent 2 → Agent 3 → Agent 4 → Agent 5 → Agent 6 → Memo
        (Claude)   (GPT)     (Claude)   (Grok)    (Gemini)   (Claude)
```

### Intermediate (v2.1): Parallelized US Chain

```
Query → Agent 1 → [Agent 2 ‖ Agent 3 ‖ Agent 4] → Divergence → Agent 5 → Agent 6 → Memo
```

### Target (v2.2): Adaptive Multi-Jurisdictional

```
Query
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR AGENT (Claude Opus 4.6)                        │
│  - Assesses query scope, complexity, and jurisdiction(s)     │
│  - Decomposes into sub-tasks                                 │
│  - Spawns parallel jurisdiction branches as needed            │
│  - Manages agent budget (token/cost ceiling per run)          │
│  - Presents cost estimate to user for confirmation            │
└──────────┬──────────────────────┬──────────────────┬─────────┘
           │                      │                  │
     ┌─────▼─────┐        ┌──────▼──────┐    ┌──────▼──────┐
     │ US Branch  │        │ EU Branch   │    │ GCC Branch  │
     │ (v2.1      │        │ (EUR-Lex    │    │ (Sharia +   │
     │  parallel  │        │  grounded,  │    │  UAE/Saudi   │
     │  chain)    │        │  GDPR/AI    │    │  portals)   │
     │            │        │  Act focus) │    │             │
     └─────┬─────┘        └──────┬──────┘    └──────┬──────┘
           │                      │                  │
           │  ┌───────────────────┘──────────────────┘
           │  │
     ┌─────▼──▼──────┐
     │ INTRA-BRANCH   │
     │ DIVERGENCE     │  ← v2.1 divergence scoring runs within each branch
     │ SCORING        │
     └───────┬────────┘
             │
      ┌──────▼──────┐
      │ CONVERGENCE  │
      │ CHECKER      │  ← v2.2 cross-jurisdiction reconciliation
      │ (Gemini Pro) │
      └──────┬──────┘
             │
      ┌──────▼──────┐
      │ SYNTHESIS    │
      │ DRAFTER      │
      │ (Claude Opus)│
      │ + vote data  │
      │ + convergence│
      │   matrix     │
      └──────┬──────┘
             │
             ▼
     Multi-Jurisdictional
     IRAC Memo
```

### Key Architectural Principles

1. **Dynamic routing** — Not all queries need all branches. A pure US contract question skips EU/GCC entirely.
2. **Parallel execution** — Both within branches (v2.1 fan-out) and across branches (v2.2 jurisdiction parallelism).
3. **Budget-aware** — Orchestrator respects per-run cost ceiling (e.g., $2.00 max). Presents estimate before execution.
4. **Backward compatible** — US-only queries still run the v2.1 parallel chain with identical output.
5. **Incremental rollout** — Each jurisdiction branch is an independent module that can be added/removed.
6. **Resilient** — Retry, fallback, timeout at every agent. Graceful degradation, never silent failure.
7. **Observable** — Full cost/token/duration trace per agent, divergence scores, confidence ratings, all via WebSocket.

---

## New Agents (v2.2)

### Agent 0: Orchestrator (NEW)

| Parameter | Value |
|-----------|-------|
| **Role** | Pipeline Orchestrator |
| **LLM** | Claude Opus 4.6 |
| **Temperature** | 0.1 |
| **Purpose** | Assess query scope, detect jurisdictions, decompose into sub-tasks, spawn branches, estimate cost |

The Orchestrator replaces the current fixed entry point. It receives the raw user query and produces a structured execution plan:

```json
{
  "jurisdictions_detected": ["US", "EU"],
  "complexity": "high",
  "branches": ["us_standard", "eu_gdpr"],
  "skip_branches": ["gcc_sharia"],
  "estimated_agents": 8,
  "estimated_cost": "$1.10 - $1.50",
  "estimated_duration_seconds": "40 - 90",
  "decomposition": [
    "Research US securities law implications",
    "Analyze EU AI Act classification for the platform",
    "Reconcile US/EU regulatory conflicts"
  ],
  "human_review_recommended": false
}
```

The frontend presents this estimate to the user for confirmation before execution begins.

### Agent J1: Jurisdiction Router (NEW)

| Parameter | Value |
|-----------|-------|
| **Role** | Jurisdiction Classifier |
| **LLM** | Gemini Flash (latest stable) |
| **Temperature** | 0.0 |
| **Purpose** | Detect legal jurisdiction(s) from query keywords, entities, and context |

Lightweight classification agent. Runs in <1 second. Detects jurisdiction signals:
- Keywords: "Sharia", "GDPR", "Article I Section 10", "DIFC", "EU AI Act"
- Entities: Country names, court names, regulatory bodies
- Context: Currency references, language, legal system terminology

Output: List of applicable jurisdictions with confidence scores.

### Agent EU1: EU/Continental Law Specialist (NEW)

| Parameter | Value |
|-----------|-------|
| **Role** | EU & Continental Law Specialist |
| **LLM** | Claude Sonnet 4.6 (multilingual, cost-efficient for deep analysis) |
| **Temperature** | 0.2 |
| **Tools** | EUR-Lex API, UK Legislation.gov.uk API |
| **Timeout** | 45s |
| **Fallback** | GPT-5.x |
| **Purpose** | Analyze EU directives, regulations, GDPR, AI Act, PSD2, consumer law |

Backstory:
> You are an expert in European Union law with specialization in EU directives, regulations, and the harmonization of national laws across member states. You analyze through the lens of the TFEU, the Charter of Fundamental Rights, and CJEU jurisprudence. You have deep expertise in GDPR, the EU AI Act (phased 2025-2027), PSD2 payments regulation, and MiCA crypto asset regulation. You always cite official EUR-Lex references with CELEX numbers. You never fabricate EU legislation or CJEU case citations. End your analysis with a one-sentence Position Summary stating your overall conclusion.

### Agent ME1: Middle East/GCC & Sharia Expert (NEW)

| Parameter | Value |
|-----------|-------|
| **Role** | GCC Regulatory & Islamic Finance Specialist |
| **LLM** | Grok 4.20 (real-time regulatory updates via X data) |
| **Temperature** | 0.2 |
| **Tools** | UAE Federal Legal Portal API, bulk Sharia text corpus (pgvector RAG) |
| **Timeout** | 45s |
| **Fallback** | Claude Sonnet 4.6 |
| **Purpose** | Sharia compliance, UAE/Saudi regulations, DIFC/ADGM common-law enclaves, Islamic finance |

Backstory:
> You are a specialist in Gulf Cooperation Council legal systems with deep expertise in Islamic finance principles (riba prohibition, gharar avoidance, mudarabah/musharakah structures). You understand the dual legal framework of UAE — federal civil law alongside DIFC and ADGM common-law enclaves. You are current on SDAIA AI ethics guidelines, UAE PDPL data protection, and Saudi Capital Markets Authority regulations. You always distinguish between Sharia interpretive opinions (which vary by madhab) and codified statutory requirements. You never fabricate fatwas, Sharia board rulings, or Gulf regulatory citations. End your analysis with a one-sentence Position Summary stating your overall conclusion.

### Agent IC1: International Convergence Checker (NEW)

| Parameter | Value |
|-----------|-------|
| **Role** | Cross-Jurisdiction Reconciliation Specialist |
| **LLM** | Gemini 3.1 Pro (strong structured reasoning) |
| **Temperature** | 0.3 |
| **Timeout** | 30s |
| **Fallback** | Claude Sonnet 4.6 |
| **Purpose** | Identify conflicts between jurisdictional analyses, flag preemption issues, produce convergence matrix |

Backstory:
> You are an international legal harmonization expert. You identify where legal conclusions from different jurisdictions conflict, where one jurisdiction's requirements preempt another's, and where compliance with multiple regimes simultaneously is possible or impossible. You produce a clear "convergence matrix" showing compatible and incompatible requirements. You never assume harmonization where genuine conflicts exist.

---

## Governance Agents (v2.2)

### Agent GA1: Guardian Agent (Anomaly Monitor)

| Parameter | Value |
|-----------|-------|
| **Role** | Pipeline Health Monitor |
| **LLM** | Gemini Flash (latest stable, cost-optimized) |
| **Temperature** | 0.0 |
| **Runs** | Parallel to entire pipeline — does NOT block execution |
| **Timeout** | N/A (runs continuously during pipeline) |
| **Purpose** | Monitor all pipeline runs for anomalies and escalate to human-in-the-loop |

The Guardian Agent is distinct from the rule-based auto-flagging in Phase 3 (Human-in-the-Loop). Where HITL uses static keyword/threshold triggers, the Guardian uses continuous observation across the full pipeline execution:

**Monitored Signals:**
- Divergence score trending higher than historical average for this query category
- Confidence drops mid-pipeline (e.g., Agent 3 confident but Agent 5 suddenly LOW)
- Cost overrun vs. Orchestrator's pre-run estimate (>150% of budget)
- Unusual agent timing (e.g., Agent 1 returns in <2s suggesting empty CourtListener results)
- Citation density anomalies (e.g., synthesis has fewer citations than expected for query complexity)
- Repeated fallback activations within a single run

**Escalation Actions:**
- LOW: Add annotation to pipeline trace ("Guardian noted: Agent 5 confidence drop")
- MEDIUM: Flag run for human review with specific concern
- HIGH: Inject warning into synthesis prompt ("Guardian alert: citation verification failed for 3+ sources — note limitations explicitly")

**Market Context:** Gartner projects guardian agents will capture 10-15% of the agentic market by 2030. Building it in now positions Lex Intelligence as governance-first.

### Agent CA1: Compliance & Risk Agent (EU AI Act Self-Classification)

| Parameter | Value |
|-----------|-------|
| **Role** | Regulatory Self-Compliance Evaluator |
| **LLM** | Claude Sonnet 4.6 |
| **Temperature** | 0.1 |
| **Runs** | Post-synthesis (evaluates final output) |
| **Timeout** | 20s |
| **Purpose** | Evaluate whether our own pipeline output meets regulatory requirements for AI-generated legal content |

This agent is fundamentally different from Agent EU1 (which analyzes user queries about EU law). CA1 evaluates whether **our output** meets regulatory standards for AI systems producing consequential legal analysis.

**Classification:** Lex Intelligence likely qualifies as high-risk under EU AI Act Article 6 when producing legal opinions that inform fintech business decisions (lending, settlements, compliance). High-risk obligations include transparency, human oversight, accuracy, and robustness — phased in August 2026-2027.

**Evaluation Criteria:**
1. **Transparency**: Does the output clearly identify itself as AI-generated? Are agent contributions visible?
2. **Human oversight**: Is human review appropriately flagged for high-stakes conclusions?
3. **Accuracy indicator**: Are confidence ratings included? Are unverifiable claims flagged?
4. **Source traceability**: Can every claim be traced to a specific agent and source?
5. **Bias check**: Does the output show provider-diversity (not single-model dominance)?

**Output:**
```json
{
  "eu_ai_act_compliance": "PASS",
  "transparency_score": 0.95,
  "human_oversight_required": true,
  "accuracy_indicators_present": true,
  "source_traceability": "FULL",
  "compliance_notes": "All citations verifiable. Confidence = MEDIUM on Section 4c — human review recommended.",
  "gdpr_data_minimization": "PASS",
  "sdaia_ethics_alignment": "NOT_EVALUATED"
}
```

This agent future-proofs for EU expansion (v2.2) and positions us for compliance certification.

---

## Proactive Watch Agents (v2.3)

### Concept: Reactive → Proactive Legal Intelligence

Current pipeline: User asks question → Pipeline produces memo (reactive).
Watch Agents: User subscribes to topics → System monitors → Pushes alerts when law changes (proactive).

### Architecture

```
User Subscription: "Monitor precious metals lending regulations"
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  WATCH AGENT (Grok 4.20, real-time X data)            │
│  - Scans X Firehose for regulatory signals             │
│  - Monitors CourtListener for new opinions              │
│  - Checks EUR-Lex for new directives (if EU sub)        │
│  - Runs on schedule: every 6 hours                      │
│                                                          │
│  IF change detected:                                     │
│    → Summarize change (1 paragraph)                      │
│    → Assess impact on subscriber's domain                │
│    → Push notification (email/Slack/portal)               │
│    → Offer: "Run full Lex Intelligence analysis? ($X)"   │
└──────────────────────────────────────────────────────┘
```

### User Subscription Model

Users subscribe to domain-specific watch topics:
- Constitutional tender / precious metals regulations
- State lending license changes
- UCC Article 9 amendments
- GDPR enforcement actions
- EU AI Act implementation updates
- UAE/DIFC fintech regulatory changes

### Cost Model

- Watch Agent scan: ~$0.02-$0.05 per check (Grok Flash for classification)
- 4 checks/day × 30 days = $2.40-$6.00/month per subscription
- Full pipeline run on detection: standard per-run pricing

### Timeline

v2.3 feature — after v2.2 multi-jurisdictional pipeline is stable. Requires Grok 4.20 API (real-time X data) and CourtListener bulk hybrid (for new opinion detection).

---

## New External Data Sources

### EUR-Lex API

| Parameter | Value |
|-----------|-------|
| **URL** | `https://eur-lex.europa.eu/eurlex-ws/` |
| **Coverage** | EU treaties, regulations, directives, decisions, CJEU case law |
| **Format** | REST API with SPARQL endpoint |
| **Auth** | Public (no key required for basic search) |
| **Integration** | Tool for EU1 agent, similar to CourtListener for US agents |
| **Open Question** | Rate limits? Batch research impact? Test before v2.2-beta1. |

### UAE Federal Legal Portal

| Parameter | Value |
|-----------|-------|
| **URL** | `https://elaws.moj.gov.ae/` |
| **Coverage** | UAE federal laws, ministerial decisions, executive regulations |
| **Format** | Web scraping likely required (no formal API confirmed) |
| **Auth** | Public |
| **Integration** | Tool for ME1 agent |
| **Open Question** | Formal API existence? May need scraper + cache layer. |

### Sharia Text Corpus (Bulk RAG)

| Parameter | Value |
|-----------|-------|
| **Sources** | SHARIAsource (Harvard), Usul.ai-inspired digitized texts, Al-Maktaba Al-Shamila, AAOIFI standards |
| **Coverage** | Classical Islamic jurisprudence, modern fatwa compilations, AAOIFI standards |
| **Format** | Pre-downloaded text corpus for hybrid RAG lookup |
| **Storage** | PostgreSQL pgvector store with embeddings |
| **Integration** | Retrieval tool for ME1 agent |
| **Open Question** | Licensing terms for SHARIAsource and Al-Maktaba Al-Shamila? |

### CourtListener Bulk Data (Enhanced — v2.1)

| Parameter | Value |
|-----------|-------|
| **Source** | `s3://com-courtlistener-storage/bulk-data/` |
| **Coverage** | Full US federal/state opinion snapshots |
| **Filter** | Federal appellate + SCOTUS, constitutional/monetary/UCC keywords |
| **Size** | ~1-5 GB filtered (vs. 50+ GB full) |
| **Refresh** | Quarterly cron job |
| **Integration** | Local PostgreSQL (GIN full-text index), hybrid with live API |

---

## Output Format Changes

### Current (v2.0): Single IRAC Memo

```
1. Issue Statement
2. Brief Answer
3. Applicable Law
4. Analysis
5. Conclusion
```

### Intermediate (v2.1): IRAC + Confidence + Divergence

```
1. Issue Statement
2. Brief Answer
3. Applicable Law
4. Analysis
5. Agent Consensus Summary (e.g., "4/5 favorable; 1 constitutional dissent")
6. Conclusion
7. Confidence Rating: HIGH / MEDIUM / LOW
8. Sources & Citations
```

### Target (v2.2): Multi-Jurisdictional IRAC Memo

```
1. Issue Statement
2. Brief Answer (with jurisdictional qualifications)
3. Jurisdictions Analyzed (with scope justification from Orchestrator)
4. US Analysis (if applicable)
   4a. Case Law
   4b. Statutory Framework
   4c. Constitutional Implications
   4d. US Agent Consensus: [polarity, confidence]
5. EU Analysis (if applicable)
   5a. EU Directives/Regulations (with CELEX citations)
   5b. CJEU Jurisprudence
   5c. Member State Variations
6. GCC/Middle East Analysis (if applicable)
   6a. Statutory Framework
   6b. Sharia Compliance Assessment
   6c. Free Zone (DIFC/ADGM) Considerations
7. Cross-Jurisdictional Convergence Matrix
   7a. Compatible Requirements
   7b. Conflicting Requirements
   7c. Preemption Issues
8. Litigation/Risk Assessment (per jurisdiction)
9. Conclusion & Recommendations
10. Confidence Ratings (per section: HIGH/MEDIUM/LOW)
11. Sources & Citations (organized by jurisdiction)
```

---

## Hallucination Mitigation (Extended — All Phases)

### v2.0 Baseline (6 layers)

1. Agent-level backstories (never fabricate citations)
2. CourtListener grounding (real API data)
3. Cross-model validation (4 providers)
4. Sequential building (each builds on verified prior output)
5. Stress testing (Agent 5 challenges prior conclusions)
6. Synthesis constraint (Agent 6 cannot add new sources)

### v2.1 Additions

7. **Position summaries** — Every agent outputs explicit 1-2 sentence conclusion for automated comparison
8. **Embedding-based divergence scoring** — Cosine similarity check before synthesis
9. **Divergence voting** — Lightweight judge aggregates consensus/dissent
10. **Human-in-the-loop** — Auto-flagged runs routed for expert review
11. **Bulk hybrid grounding** — Local DB reduces reliance on single API

### v2.2 Additions

12. **Jurisdiction-specific "never fabricate" rules** — CELEX numbers for EU, case references for GCC courts
13. **Cross-jurisdiction convergence checking** — Dedicated agent reconciles conflicts
14. **Confidence per jurisdiction** — Independent HIGH/MEDIUM/LOW per section
15. **Source separation** — EU sources never cited as US authority and vice versa
16. **Human-in-loop mandatory** — Cross-border queries automatically flagged

### v2.2 Governance Additions

17. **Guardian Agent** — Continuous anomaly monitoring parallel to all runs
18. **Compliance Agent** — EU AI Act self-classification on every output
19. **Validator Agent** — Ground truth checking against known-correct databases
20. **Weighted explainability** — Agent contribution attribution in final memo

### v2.3 Additions

21. **Self-evolving memory** — Divergence resolution patterns learned across runs
22. **Proactive monitoring** — Watch Agents detect regulatory changes before users ask

---

## Interoperability & Ecosystem Integration (v2.2-v2.3)

### Problem

Lex Intelligence currently operates as a closed system. The 2026 agentic AI landscape is moving toward "super agent" ecosystems where agents from different vendors collaborate. Three emerging protocols enable this:

| Protocol | Owner | Purpose | Maturity (Feb 2026) |
|----------|-------|---------|---------------------|
| **MCP** (Model Context Protocol) | Anthropic | Standardized context sharing between AI systems | Production-ready, widely adopted |
| **ACP** (Agent Communication Protocol) | IBM | Agent-to-agent messaging and task delegation | Early adoption |
| **A2A** (Agent-to-Agent) | Google | Cross-platform agent handoffs | Beta |

### Integration Plan

**v2.2: MCP First (Anthropic ecosystem)**
- Expose Lex Intelligence as an MCP server: external agents can request legal analysis via standardized protocol
- Consume external MCP tools: Clio (case management), vLex (legal research), user-uploaded contracts
- This enables Claude-based systems to invoke Lex Intelligence as a tool

**v2.3: A2A + ACP for Cross-Platform**
- Register Lex Intelligence as a discoverable agent in A2A directories
- Accept task delegations from enterprise orchestrators (e.g., "analyze this contract for compliance" from a Salesforce agent)
- Enable user-uploaded documents as pipeline input (contracts, filings, regulatory notices)

### Architecture

```
External System (Clio, vLex, user agent)
    │
    ▼ (MCP / A2A / ACP)
┌──────────────────────────┐
│ Lex Intelligence API      │
│ Protocol Adapter Layer    │
│ (translates MCP/A2A/ACP  │
│  to internal pipeline     │
│  run request)             │
└──────────┬───────────────┘
           │
           ▼
    Standard Pipeline Execution
```

### Security

- All external protocol calls authenticated (API key + JWT)
- Rate-limited separately from internal usage
- User-uploaded documents scanned before processing
- No external agent can modify pipeline configuration — read-only execution

---

## Weighted Explainability — "Why This Conclusion?" (v2.2)

### Problem

The current pipeline shows per-agent output in the trace, but the final synthesis memo doesn't explain which agents most influenced the conclusion. Users (especially legal professionals) need to understand attribution.

### Implementation

Agent 6 (Synthesis) receives a new prompt addition:

> After your conclusion, add an "Agent Attribution" section. For each major point in your analysis, note which agent's work most influenced that point. Use a 0.0-1.0 weight reflecting relative influence. Example: "Constitutional analysis (Agent 3, weight 0.42) was the primary driver of this conclusion, supported by case law research (Agent 1, weight 0.28) and statutory interpretation (Agent 2, weight 0.18). Litigation risk assessment (Agent 5, weight 0.12) identified no viable counterarguments."

### Output Addition to IRAC Memo

```
12. Agent Attribution
    - Issue framing: Agent 1 (Research, 0.35), Agent 3 (Constitutional, 0.40)
    - Legal reasoning: Agent 3 (Constitutional, 0.45), Agent 2 (Statutory, 0.30)
    - Risk assessment: Agent 5 (Litigation, 0.55), Agent 4 (Contract, 0.25)
    - Overall conclusion driver: Agent 3 (Constitutional Law Expert)
```

### Benefits

- Transparency: Users see which expertise shaped each section
- Trust: Weighted attribution builds confidence in multi-agent output
- Debugging: If conclusions seem wrong, attribution points to the responsible agent
- EU AI Act compliance: Directly addresses transparency requirements

---

## Domain-Specific Adapters (v2.3)

### Concept

Rather than fine-tuning frontier models (expensive, maintenance burden), use lightweight adaptation techniques to boost accuracy on fintech sub-domains.

### Approach: Curated In-Context Example Sets

For each fintech sub-domain, maintain a curated set of 10-20 exemplar query-response pairs that demonstrate correct reasoning patterns:

| Domain | Example Count | Key Patterns |
|--------|--------------|-------------|
| Constitutional tender (Art. I §10) | 15-20 | State vs. federal preemption, legal tender clause interpretation, precious metals as money |
| UCC Article 9 (secured transactions) | 10-15 | Perfection requirements, priority disputes, chattel paper |
| Lending compliance (TILA, ECOA, HMDA) | 10-15 | Disclosure requirements, adverse action notices, fair lending |
| Settlement coordination | 8-10 | Escrow requirements, title insurance, disbursement timing |
| Islamic finance (v2.2) | 10-15 | Riba prohibition, mudarabah structures, AAOIFI compliance |

### Integration

The Orchestrator Agent selects relevant example sets based on query classification and injects them as few-shot context for the most relevant agents. This is dynamic — different query categories get different example sets without model retraining.

### Future: LoRA Adapters

If in-context examples prove insufficient (e.g., for very specialized Sharia finance reasoning), evaluate LoRA/QLoRA fine-tuning on open-weight models (e.g., Qwen 3.5, Llama-4) as cost-effective specialist fallbacks. Decision point: v2.3 planning.

---

## Agentic Liability Framework

### Problem

"Who owns autonomous errors?" is a 2026 hot topic as agentic AI moves into consequential domains. Lex Intelligence produces legal analysis that informs real business decisions (lending, settlements, compliance). Clear liability boundaries are essential.

### Liability Principles

1. **Advisory only**: All Lex Intelligence output is advisory. It does not constitute legal advice and does not create an attorney-client relationship.

2. **Human authority**: No Lex Intelligence output should be used as the sole basis for binding legal decisions. Human review by qualified counsel is required for all consequential actions.

3. **Transparency of limitations**: Every output includes confidence ratings, divergence data, and explicit flags for areas of uncertainty. Users are never misled about AI limitations.

4. **Error attribution**: Pipeline trace (per-agent output, citations, divergence scores) provides full auditability. If an error occurs, the trace identifies which agent(s) produced the incorrect analysis and which model was responsible.

5. **No guarantee of completeness**: Lex Intelligence searches available databases and applies available models. It does not guarantee coverage of all relevant law, cases, or regulatory changes.

### Disclaimer Template (Appended to Every Output)

> **DISCLAIMER**: This analysis was generated by Lex Intelligence, a multi-agent AI legal research pipeline. It is provided for informational purposes only and does not constitute legal advice. No attorney-client relationship is created. AI-generated legal analysis may contain errors, omissions, or outdated information. All conclusions should be reviewed by qualified legal counsel before any action is taken. Confidence ratings and agent attribution are provided for transparency — they reflect AI self-assessment, not legal certainty. Calculus Holdings LLC and its affiliates assume no liability for decisions made based on this output.

### EU AI Act Alignment

The Compliance Agent (CA1) evaluates each output against EU AI Act requirements and flags when additional disclaimers or human review are required. This framework is designed to satisfy Article 14 (human oversight) and Article 13 (transparency) obligations for high-risk AI systems.

### Insurance Consideration

As Lex Intelligence scales to external users (v2.3+ SaaS), evaluate professional liability / E&O insurance coverage for AI-generated legal analysis. This is an emerging insurance product in 2026 — consult with broker.

---

## Go-to-Market Strategy (v2.2 → v2.3)

### Phased Rollout

| Phase | Audience | Timeline | Pricing |
|-------|----------|----------|---------|
| **Internal** | Calculus Holdings entities (CT, TILT, Eureka, DMC) | v2.0-v2.1 (Now - May 2026) | Internal cost allocation |
| **Beta Partners** | 5-10 fintech firms (invite-only) | v2.2 (June - Oct 2026) | Free / subsidized |
| **Public SaaS** | Fintech legal teams, solo practitioners, compliance officers | v2.3 (Q1 2027) | $99-$299/mo |

### Pricing Strategy

Position as "independent multi-model fintech legal agent" vs. $400-$1,000+/mo enterprise incumbents (Harvey, CoCounsel).

| Tier | Price | Includes | Target |
|------|-------|----------|--------|
| **Starter** | $99/mo | 50 pipeline runs, US-only, email support | Solo practitioners, small firms |
| **Professional** | $199/mo | 200 runs, US + EU, priority support, Watch Agents (2 topics) | Mid-size fintech teams |
| **Enterprise** | $299/mo + per-run overage | Unlimited runs, all jurisdictions, dedicated support, RBAC, SSO | Legal departments, compliance teams |

Per-run overage: $1.50 for US-only, $2.50 for multi-jurisdictional.

### Competitive Differentiation

| Feature | Lex Intelligence | Harvey | CoCounsel | HAQQ |
|---------|-----------------|--------|-----------|------|
| Multi-provider cross-validation | ✅ 4 LLMs | ❌ Single | ❌ GPT-only | ❌ Single |
| Per-agent cost transparency | ✅ Full trace | ❌ Black box | ❌ Black box | ❌ Limited |
| Fintech specialization | ✅ Deep | ⚠️ General | ⚠️ General | ⚠️ Limited |
| Multi-jurisdictional (US+EU+GCC) | ✅ v2.2 | ⚠️ US-heavy | ⚠️ US-heavy | ✅ |
| Governance-first (Guardian + Compliance) | ✅ Built-in | ❌ | ❌ | ❌ |
| Price per month | $99-$299 | $500+ | $400+ | Unknown |

### ROI Transparency Dashboard

Track and expose to users:
- Hours of legal research avoided per run (estimated: 2-6 hours at $200-$500/hr attorney rate)
- Cost per run vs. equivalent attorney time
- Risk mitigation score (based on confidence + divergence + human review)
- Anonymized benchmarks (aggregate accuracy across all users, opt-in)

---

## Cost Projections (Revised with Ranges)

### US-Only Query (v2.1 parallel chain)

| Component | Est. Cost Range |
|-----------|----------------|
| Agent 1 (Opus 4.6, Research) | $0.15 - $0.25 |
| Agents 2-4 (parallel) | $0.08 - $0.15 |
| Divergence scorer | $0.002 - $0.01 |
| Agent 5 (Gemini 3.1 Pro) | $0.01 - $0.03 |
| Agent 6 (Opus 4.6, Synthesis) | $0.25 - $0.45 |
| **Total** | **$0.50 - $0.90** |

### Multi-Jurisdictional Query (US + EU)

| Component | Est. Cost Range |
|-----------|----------------|
| Orchestrator (Opus 4.6) | $0.06 - $0.12 |
| Jurisdiction Router (Flash) | $0.001 |
| US Branch (parallel) | $0.50 - $0.90 |
| EU Specialist (Sonnet 4.6) | $0.08 - $0.18 |
| Intra-branch divergence | $0.004 - $0.02 |
| Convergence Checker (Gemini Pro) | $0.02 - $0.05 |
| Synthesis enhanced (Opus 4.6) | $0.30 - $0.50 |
| **Total** | **$1.00 - $1.80** |

### Full Tri-Jurisdictional Query (US + EU + GCC)

| Component | Est. Cost Range |
|-----------|----------------|
| Orchestrator (Opus 4.6) | $0.08 - $0.15 |
| Jurisdiction Router (Flash) | $0.001 |
| US Branch (parallel) | $0.50 - $0.90 |
| EU Specialist (Sonnet 4.6) | $0.08 - $0.18 |
| GCC/Sharia Specialist (Grok 4.20) | $0.05 - $0.12 |
| Intra-branch divergence (x3) | $0.006 - $0.03 |
| Validator Agent (Gemini Pro) | $0.02 - $0.05 |
| Convergence Checker (Gemini Pro) | $0.03 - $0.07 |
| Guardian Agent (Flash, parallel) | $0.003 - $0.01 |
| Compliance Agent (Sonnet 4.6) | $0.03 - $0.08 |
| Synthesis enhanced (Opus 4.6) | $0.35 - $0.55 |
| **Total** | **$1.20 - $2.20** |

### Governance Overhead Per Run

The Guardian, Validator, and Compliance agents add approximately $0.05-$0.14 per run — a 5-7% governance tax that buys audit trail, ground-truth verification, and regulatory compliance. This is significantly cheaper than the alternative: post-hoc human review of every output.

---

## Implementation Timeline (Revised)

| Phase | Deliverable | Dependency | Target |
|-------|------------|-----------|--------|
| **v2.0.1** | Model string upgrades (Opus 4.6, Gemini stable) | None — config change only | **March 2026** |
| **v2.1-alpha** | Intra-pipeline parallelism (fan-out Agents 2-4) | CrewAI parallel task support | March 2026 |
| **v2.1-beta1** | Divergence scoring + voting mechanism | Embedding model selection | April 2026 |
| **v2.1-beta2** | Human-in-the-loop (auto-flagging + review queue) | Slack integration | April 2026 |
| **v2.1-beta3** | CourtListener monitoring + bulk hybrid | S3 bulk download + PostgreSQL | April 2026 |
| **v2.1-rc** | Resilience patterns (retry, fallback, timeout) | All providers tested | May 2026 |
| **v2.1.0** | Grok 4.20 API upgrade, RBAC, team platform, feedback loop storage | xAI API GA (est. March) | **May 2026** |
| **v2.2-alpha** | Orchestrator Agent + Jurisdiction Router | v2.1 stable | June 2026 |
| **v2.2-beta1** | EU Branch (EUR-Lex integration) + Compliance Agent (CA1) | EUR-Lex API testing | July 2026 |
| **v2.2-beta2** | GCC Branch (UAE portal + Sharia corpus) + Guardian Agent (GA1) | Corpus preparation | August 2026 |
| **v2.2-beta3** | Validator Agent + weighted explainability | Bulk DB indexed | September 2026 |
| **v2.2-rc** | Convergence Checker + enhanced synthesis + liability framework | All branches tested | September 2026 |
| **v2.2.0** | Production release, multi-jurisdictional, governance-first | Full integration test | **October 2026** |
| **v2.2.1** | MCP server exposure + Clio/vLex integration | MCP adapter layer | November 2026 |
| **v2.2.2** | Domain-specific adapter sets (constitutional tender, UCC, lending) | Example curation | December 2026 |
| **v2.3-alpha** | Proactive Watch Agents (regulatory monitoring) | Grok 4.20 API + bulk hybrid | January 2027 |
| **v2.3-beta** | A2A/ACP interoperability + user-uploaded document input | Protocol adapter layer | February 2027 |
| **v2.3.0** | Public SaaS launch, ROI dashboard, self-evolving memory mature | Beta partner feedback | **March 2027** |

---

## Prerequisites

Before v2.2 development begins:

1. ✅ v2.0 backend complete with 6-agent Lex Intelligence
2. ⬜ v2.0 React frontend shipped and stable
3. ⬜ v2.0.1 model strings upgraded to current frontier
4. ⬜ v2.1 intra-pipeline parallelism deployed
5. ⬜ v2.1 divergence scoring operational
6. ⬜ v2.1 human-in-the-loop system deployed
7. ⬜ v2.1 CourtListener monitoring + bulk hybrid operational
8. ⬜ v2.1 resilience patterns (retry/fallback/timeout) deployed
9. ⬜ v2.1 feedback loop storage (pipeline_run_memory table) deployed
10. ⬜ v2.1 team platform with RBAC deployed
11. ⬜ Grok 4.20 API available and integrated
12. ⬜ EUR-Lex API access tested and documented
13. ⬜ UAE Federal Legal Portal access method confirmed
14. ⬜ Sharia text corpus sourced, cleaned, and embedded
15. ⬜ PostgreSQL pgvector store configured for corpus retrieval
16. ⬜ `BasePipeline` extended to support parallel branch execution
17. ⬜ WebSocket events extended for multi-branch progress streaming
18. ⬜ Liability disclaimer template reviewed by counsel
19. ⬜ EU AI Act high-risk classification confirmed (legal opinion)
20. ⬜ MCP server SDK evaluated for protocol adapter layer

---

## Open Questions

### Technical
1. **Sharia corpus licensing** — What are the licensing terms for SHARIAsource and Al-Maktaba Al-Shamila texts?
2. **EUR-Lex rate limits** — Does the public API have rate limits that affect batch research?
3. **UAE portal API** — Is there a formal API, or does this require web scraping?
4. **DIFC/ADGM case law** — These common-law enclaves have their own court systems. Separate tool needed?
5. **Multilingual prompts** — Should EU agent receive prompts in the source language for better statutory analysis?
6. **Agent 2 model decision** — Sonnet 4.5 vs GPT-5.x for statutory analysis? Need head-to-head eval on sample queries.
7. **Gemini 3.1 Pro for Agent 5** — Confirm pricing stable at ~$2-$4.50 per M input before committing.
8. **Free Law Project bulk agreement** — Contact early if v2.1 team scale exceeds 5,000 queries/hour.
9. **Open-source fallback models** — DeepSeek-R1 or Qwen 3.5 as self-hosted cheap reasoning fallback? Evaluate.
10. **Feedback loop bias risk** — Could self-evolving memory create confirmation bias? Need decay function or periodic reset.
11. **LoRA feasibility** — Is fine-tuning cost-justified for fintech sub-domains, or are curated example sets sufficient?

### Governance & Legal
12. **EU AI Act classification** — Confirm high-risk classification with external counsel before building Compliance Agent.
13. **Agentic liability insurance** — Emerging E&O products for AI-generated legal analysis — evaluate coverage options.
14. **Disclaimer sufficiency** — Is the current disclaimer template legally adequate? Varies by jurisdiction.
15. **Data residency** — EU users may require data processing within EU. Affects infrastructure for v2.3 SaaS.

### Commercial
16. **Cost ceiling UX** — How should the frontend display estimated cost before the user commits to a multi-jurisdictional run?
17. **Beta partner selection** — Which 5-10 fintech firms for v2.2 beta? Criteria: size, jurisdiction needs, feedback quality.
18. **Pricing validation** — $99-$299/mo competitive? Need market research against Harvey/CoCounsel actual street pricing.
19. **Watch Agent demand** — Do fintech legal teams actually want proactive monitoring? Validate before building v2.3.

---

## Appendix A: Grok 4.20 Review Summary

Grok 4.20 Heavy conducted a multi-turn architectural review of Lex Intelligence Ultimate across four dimensions:

| Dimension | Score | Key Feedback |
|-----------|-------|-------------|
| **Overall Design** | 8.5/10 → 9.5/10 (with upgrades) | "One of the more thoughtful and realistic multi-agent setups in 2026" |
| **Hallucination Defense** | Excellent | "Far better than most naive agent pipelines" |
| **Provider Diversity** | Strong | "Smart for reducing correlated failures/biases" |
| **Cost Realism** | Needs correction | $0.77 → $0.80-$1.20 realistic |
| **Model Currency** | Behind frontier | 3-9 months behind February 2026 releases |
| **Missing Infrastructure** | 5 gaps identified | Parallelism, divergence, HITL, monitoring, resilience |

All infrastructure gaps are now addressed. Additional Grok recommendations incorporated in Rev 3.0: self-evolving memory, Validator Agent, Guardian Agent, Compliance Agent, interoperability protocols, domain adapters, explainability, go-to-market strategy, and liability framework.

---

## Appendix B: Complete Agent Census

### v2.0 Pipeline Agents (6)

| # | Agent | Model | Role |
|---|-------|-------|------|
| 1 | Legal Research Specialist | Claude Opus 4.6 | Case law research, CourtListener grounding |
| 2 | Statutory Analyst | Sonnet 4.5 / GPT-5.x | Statute/regulation analysis |
| 3 | Constitutional Law Expert | Claude Opus 4.6 | Constitutional implications, Art. I §10 |
| 4 | Contract & Commercial | Grok 4.20 | UCC, contract interpretation |
| 5 | Litigation Strategy Advisor | Gemini 3.1 Pro | Devil's advocate, risk assessment |
| 6 | Legal Synthesis & Opinion | Claude Opus 4.6 | IRAC memo drafting |

### v2.2 New Pipeline Agents (+7)

| # | Agent | Model | Role |
|---|-------|-------|------|
| 0 | Orchestrator | Claude Opus 4.6 | Dynamic routing, cost estimation |
| J1 | Jurisdiction Router | Gemini Flash | Lightweight jurisdiction classification |
| EU1 | EU/Continental Law | Claude Sonnet 4.6 | EUR-Lex grounded EU analysis |
| ME1 | GCC/Sharia Expert | Grok 4.20 | Islamic finance, UAE/Saudi regs |
| IC1 | Convergence Checker | Gemini 3.1 Pro | Cross-jurisdiction reconciliation |
| GA1 | Guardian Agent | Gemini Flash | Continuous anomaly monitoring |
| CA1 | Compliance Agent | Claude Sonnet 4.6 | EU AI Act self-classification |

### v2.2 Non-LLM Components (+2)

| # | Component | Type | Role |
|---|-----------|------|------|
| DS | Divergence Scorer | Embedding + rules | Intra-pipeline agreement detection |
| VA | Validator Agent | Gemini 3.1 Pro | Ground truth citation checking |

### v2.3 Watch Agents (+1)

| # | Agent | Model | Role |
|---|-------|-------|------|
| WA | Watch Agent(s) | Grok 4.20 | Proactive regulatory monitoring |

### Total Agent Count by Version

| Version | Pipeline Agents | Governance Agents | Watch Agents | Total |
|---------|----------------|-------------------|-------------|-------|
| v2.0 | 6 | 0 | 0 | **6** |
| v2.1 | 6 + divergence scorer | 0 | 0 | **7** |
| v2.2 | 13 + divergence scorer + validator | 2 (Guardian + Compliance) | 0 | **16** |
| v2.3 | 13 + divergence scorer + validator | 2 | 1+ (per subscription) | **17+** |

### Coding Agents (Poly-Agent Orchestration — Unchanged)

| Agent | Role |
|-------|------|
| Claude Opus | Architecture & Directives |
| GitHub Copilot Agent | PR Generation |
| Codespace Copilot Chat | Terminal & Debug |
| Grok | Boilerplate & Infrastructure |

---

*This document will be updated as v2.1 development progresses and prerequisites are resolved.*

*Generated: February 17, 2026 (original) / February 25, 2026 (rev 2.0) / February 25, 2026 (rev 3.0)*
*Project Lead: Sean Grady, CEO*
*Architecture: Claude Opus 4.6*
*Competitive Intelligence + Review: Grok 4.20 Heavy*
