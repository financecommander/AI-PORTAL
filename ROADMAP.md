# CALCULUS LABS AI PORTAL — ROADMAP

**Owner**: Calculus Holdings LLC  
**Current Version**: v2.1  
**Goal**: Evolve from internal specialist chat and pipeline runner into the intelligent control plane for the Sovereign Enterprise — declarative multi-agent orchestration, institutional-grade legal/financial intelligence, and self-improving reasoning.

Last updated: February 27, 2026

## Current State (v2.1 — Deployed)

What's live today:

- **Lex Intelligence Ultimate**: 6-agent legal pipeline (GPT-4o, Grok 3 Mini, Gemini 2.5 Flash) with real-time WebSocket progress streaming
- **Calculus Intelligence**: 6-agent heterogeneous deep reasoning pipeline with cross-model validation (GPT-4o, Grok, Gemini)
- **Forge Intelligence**: registered stub for future code gen pipeline
- **4 specialist chat agents** with SSE streaming (Claude Sonnet, GPT-4o, Claude Opus, Grok)
- **Orchestra DSL foundation**: .orca YAML pipeline definitions auto-discovered and registered at startup
- Token tracking and cost logging across all providers via CrewAI/LiteLLM
- JWT auth, PostgreSQL, Docker Compose on GCP

---

## IMMEDIATE PRIORITY: Orchestra DSL Integration (v2.2)

**Status**: Foundation deployed. Loader, builder, and registry auto-discovery are live.

Orchestra lets you define pipelines in declarative YAML instead of Python. Drop an `.orca` file into `backend/pipelines/definitions/`, restart, and it appears in the UI. No code changes, no Docker rebuild for pipeline logic.

### What's built (deployed with v2.1):

- `orch_pipeline.py` — Reads YAML config, builds crewai.LLM + Agent + Task objects, returns a CrewPipeline
- `orch_loader.py` — Scans `definitions/` directory for .orca files, auto-registers each one
- `registry.py` — Updated to call Orchestra discovery on first access; hand-coded pipelines take priority on name collisions
- `financial_strategy.orca` — First Orchestra-defined pipeline (4 agents: Market Analyst, Risk Assessor, Quant Modeler, Strategist)

### What's next for Orchestra:

**Phase A — Parallel and branching execution (1 week)**

Add `flow` directive support so .orca files can declare parallel branches:

```yaml
flow:
  - decomposer >> [reasoner_a, reasoner_b]  # parallel
  - [reasoner_a, reasoner_b] >> validator   # join
  - validator >> synthesizer
```

Implementation: Parse flow directives in `orch_pipeline.py`, translate parallel branches into CrewAI's async task execution or custom `asyncio.gather()` wrapper.

**Phase B — Quality gates enforcement (1 week)**

The `gates` section in .orca files is currently parsed and stored as metadata but not enforced. Build gate evaluation into CrewPipeline's task_callback:

```yaml
gates:
  - name: confidence_check
    after: validator
    rule: "confirmed_claims / total_claims > 0.6"
    on_fail: escalate_to_human
```

Implementation: After the specified task completes, evaluate the gate rule against the task output. On failure, either log a warning, inject a re-evaluation prompt, or flag for human review via WebSocket event.

**Phase C — Model hot-swap without restart (1-2 weeks)**

File watcher on the `definitions/` directory. When an .orca file is modified, rebuild that pipeline instance without restarting the backend. Enables model upgrades (e.g., `gpt-4o` → `gpt-5`) by editing one line in YAML.

**Phase D — Convert existing pipelines to .orca (ongoing)**

Write `.orca` equivalents of `lex_intelligence.py` and `calculus_intelligence.py`. Once validated, the hand-coded Python versions become fallbacks. New pipelines should always be .orca first.

---

## Phase 0 — Stabilization & Cleanup (2-3 weeks, parallel with Orchestra)

- **Rebrand consistently** to Calculus Labs across README, docs, frontend titles, email domain checks
- **Remove legacy Streamlit** code (`app.py`, `.streamlit/`, `ui/`) — migrate any remaining views to React
- **Fix bugs** from `PRIORITY_1_FIXES.md`
- **Test coverage** >85% on WebSocket pipeline streaming and Orchestra loader
- **Internal one-pager**: "What is Calculus AI Portal?" for team and investors

---

## Phase 1 — UI Overhaul (v2.3, 2-3 weeks)

Modernize the frontend with patterns from the best AI products of 2026.

### 1A. Artifacts Pane (Claude-inspired)

Resizable right sidebar that renders pipeline outputs as rich content: markdown, code syntax highlighting, tables, structured sections. When a pipeline completes, the final output appears in the artifacts pane instead of raw text in the chat area.

Files to create: `ArtifactsPane.tsx`, `MarkdownRenderer.tsx`, `CodeBlock.tsx`

### 1B. Agent Trace Visualizer

Live timeline showing each agent's execution with model badges, duration bars, and expandable output previews. Shows parallel execution (where Orchestra enables it), contradiction flags between reasoning paths, and convergence points.

Files to create: `AgentTraceVisualizer.tsx`, `AgentTimeline.tsx`, `ModelBadge.tsx`

### 1C. Confidence & Sources Panel (Perplexity-inspired)

For Calculus Intelligence: display per-claim confidence scores from the Adversarial Validator. Show agreement/disagreement map across reasoning agents. Link to sources when the Evidence Grounder is built (Phase 3).

### 1D. Inline Output Editing (Canvas-inspired)

Click into the final synthesized output and request targeted AI edits: "make this more concise", "add tax implications", "rewrite for a non-technical audience." Sends edit request through a single-agent call back to the synthesizer.

### 1E. Pipeline Selector Upgrade

One-click switch between all registered pipelines (hand-coded + Orchestra-discovered). Show agent count, model badges, estimated cost, and a "YAML-defined" badge for Orchestra pipelines.

---

## Phase 2 — Legal & Fintech Depth + Business Integration (v2.4, 1-2 months)

### 2A. Eureka Settlement Services Integration

Add conditional trigger from Eureka: high-value precious metals transactions or instant-liquidity requests POST to `/api/v2/pipelines/run` with `pipeline_name: lex_intelligence`. Display compliance score and opinion link in portal UI.

### 2B. Confidence Scoring & Human-in-Loop

Per-agent HIGH/MEDIUM/LOW confidence with aggregated final score. When overall confidence is MEDIUM or below, or when agent divergence exceeds a threshold, trigger Slack/email alert for human review. Orchestra quality gates can enforce this declaratively.

### 2C. Lex Intelligence Agent Alignment

Upgrade model assignments as new models become available:
- Legal Research Specialist → Claude Opus (if CrewAI tool_use conflict resolved)
- Contract Specialist → Grok 4 Fast
- Add parallel branches: statutory + constitutional analysis run simultaneously after case law research

### 2D. Multi-Jurisdiction Support

Add EU Statutory Agent (GDPR, AI Act compliance) and GCC/Sharia Specialist. Define as new .orca pipelines with jurisdiction-specific tools and knowledge.

### 2E. Side-by-Side Pipeline Comparison

Run the same query through multiple pipelines simultaneously. Split-pane view comparing Lex (legal-specific) vs Calculus (general reasoning) outputs.

---

## Phase 3 — Memory, Self-Improvement & Scale (v2.5, 2-3 months)

### 3A. Persistent Reasoning Memory

Store successful reasoning traces in PostgreSQL with pgvector. When a new query resembles a past one, inject prior traces as context into the decomposer. Grok Heavy cannot do per-user persistent learning at scale.

### 3B. Post-Query Feedback Loop

After every pipeline run, a lightweight post-mortem agent evaluates: did reasoning paths converge? Were validator concerns resolved? This data adjusts routing weights — queries where Grok excels get routed to Grok, queries where Gemini excels get routed to Gemini.

### 3C. Evidence Grounder Agent

7th agent for Calculus Intelligence with web search and real-time data tools. Fact-checks claims from reasoning agents. Defined as a tool-equipped agent in the .orca file.

### 3D. Confidence-Based Cascade

Smart routing in Calculus Intelligence. Simple queries (complexity 1-4) → single model. Medium (5-7) → 3 agents. Hard (8-10) → full ensemble. The decomposer already scores complexity — this adds routing logic.

### 3E. Forge Intelligence Build-Out

Code generation pipeline: architecture design, implementation, code review, test generation, documentation. Defined in .orca format. Completes the three-pipeline suite.

### 3F. Usage & ROI Dashboard

Frontend view of per-user token costs, hours saved, confidence trends, pipeline comparison. All data already exists in PostgreSQL — just needs a React dashboard page.

---

## Phase 4 — Sovereign Enterprise Integration (v3.0, Q3-Q4 2026)

### 4A. API-First Integration Layer

Secure endpoints for DFIP Ledger, SPV Architect, Structuring Agent, Seraph Shield. Signed webhook delivery from portal to downstream agents.

### 4B. Orchestra Visual Editor

Web-based pipeline builder. Drag agents into a flow, configure models and gates, Orchestra generates the .orca YAML. The Lex Terminal concept meets Orchestra DSL.

### 4C. Execution Modes

- **Fast**: 2-3 agents, single model, sub-10s. For quick questions.
- **Standard**: full 6-agent pipeline. Current default.
- **Maximum**: 8-12 agent ensemble with multi-round debate. For highest-stakes decisions.
- **Private**: route sensitive subtasks through self-hosted models (Llama, DeepSeek-R1).

### 4D. Multi-Round Debate Protocol

After the validator identifies disputes, route them back through reasoning agents for a second round. Research shows 2-round debate resolves 80%+ of cross-model disagreements.

### 4E. Edge & Mobile Access

Responsive design + PWA support. EdgeForge toolkit integration for offline/low-latency runs.

### 4F. Compliance & Governance Hardening

EU AI Act classification (high-risk checks). Full audit trails + exportable logs. Orchestra gates enforce compliance rules declaratively. Periodic third-party security review.

### 4G. Public Beta Consideration

Phased rollout to trusted partners. Pricing tiers ($99-$499/mo) as independent multi-model fintech legal intelligence platform.

---

## Success Metrics (End of 2026)

- 95%+ test coverage on pipelines, WebSocket layer, and Orchestra loader
- Average pipeline run < 90 seconds
- >90% HIGH-confidence legal opinions on fintech queries
- Eureka → Lex call latency < 5 seconds (cached responses)
- 10+ .orca pipeline definitions in production
- Zero major security incidents

## Competitive Position

| Dimension | Grok 4 Heavy | Calculus Intelligence (fully built) |
|-----------|-------------|-------------------------------------|
| Speed | Native advantage | Competitive with cascade routing |
| Cost per query | $300/mo subscription | Pay-per-use, ~$0.15-0.25/query |
| Peak accuracy (hard tasks) | Strong | Superior via model diversity |
| Hallucination resistance | Good | Better via cross-model validation |
| Customization | None | Full persistent memory + feedback loop |
| Transparency | Black box | Full reasoning trace visible |
| Domain specialization | Generic | Lex (legal), Forge (code), custom .orca |
| Pipeline creation | Not possible | Drop a YAML file, restart, done |

## Risks & Blockers

- LLM provider API rate limits / cost spikes (mitigate: cascade routing, model diversity)
- CourtListener API quota (mitigate: bulk hybrid fallback, caching)
- CrewAI tool_use conflict with Anthropic models (mitigate: use OpenAI/Grok for tool-equipped agents)
- Team bandwidth for frontend vs backend work (mitigate: Orchestra reduces backend work per pipeline)