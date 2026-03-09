# CALCULUS LABS AI PORTAL v3.0

Private multi-LLM intelligence platform for legal, financial, and deep reasoning workflows. Features 8 LLM providers, multi-agent pipelines, knowledge distillation, Swarm GPU integration, and a permit intelligence system.

Built for Calculus Holdings — 2026.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  React 19 Frontend                       │
│  Console │ Specialists │ Pipelines │ Swarm │ LeadOps    │
├─────────────────────────────────────────────────────────┤
│                  nginx reverse proxy                     │
├─────────────────────────────────────────────────────────┤
│                  FastAPI Backend                         │
│  JWT Auth │ Chat │ Pipelines │ Distillation │ Training  │
├───────┬────────┬────────┬───────┬──────┬────────────────┤
│GPT-4o │ Claude │ Gemini │ Grok  │Llama │ DeepSeek/etc  │
├───────┴────────┴────────┴───────┴──────┴────────────────┤
│         PostgreSQL 16  │  Ollama GPU (NVIDIA L4)         │
└─────────────────────────────────────────────────────────┘
```

## LLM Providers

| Provider | Models | Notes |
|----------|--------|-------|
| OpenAI | GPT-4o, GPT-4o Mini | Primary reasoning |
| Anthropic | Claude Opus 4.6, Sonnet 4.5 | Deep analysis, code review |
| Google | Gemini 2.5 Flash | High-volume, cost-efficient |
| xAI | Grok 3 Mini | Lateral reasoning |
| DeepSeek | R1, V3.2 | Open-weight reasoning |
| Mistral | Large 3, Medium 3 | European AI |
| Groq | Llama 4 Maverick, Scout | Fast inference |
| Ollama | Llama 3.1 8B, DeepSeek R1 14B, Qwen 2.5 Coder | Local GPU, $0/token |

## Intelligence Console

Multi-model direct chat interface. Select any provider and model, with full conversation history persistence, auto-titling, and URL-shareable conversations. Supports SSE streaming across all providers.

## Intelligence Pipelines

### Lex Intelligence Ultimate

6-agent legal research and opinion drafting pipeline. Agents execute sequentially, each building on the prior output to produce a comprehensive legal memorandum.

| # | Agent | Model | Role |
|---|-------|-------|------|
| 1 | Legal Research Specialist | GPT-4o | Case law search via CourtListener API |
| 2 | Statutory Analyst | GPT-4o | Statute interpretation and regulatory analysis |
| 3 | Constitutional Law Expert | GPT-4o | Constitutional implications and civil rights |
| 4 | Contract & Commercial Law | Grok 3 Mini | Contract interpretation and UCC analysis |
| 5 | Litigation Strategy Advisor | Gemini 2.5 Flash | Case strength assessment and strategy |
| 6 | Legal Synthesis & Opinion | GPT-4o | Final opinion memorandum drafting |

### Calculus Intelligence

6-agent heterogeneous deep reasoning pipeline. Routes through three different model families and cross-validates their outputs.

| # | Agent | Model | Role |
|---|-------|-------|------|
| 1 | Query Decomposer & Router | GPT-4o | Classifies complexity, breaks into subtasks |
| 2 | Analytical Reasoner | GPT-4o | Structured step-by-step logical reasoning |
| 3 | Creative & Lateral Reasoner | Grok 3 Mini | Alternative perspectives, challenges assumptions |
| 4 | Deep Context Analyst | Gemini 2.5 Flash | Synthesizes agreement/disagreement across paths |
| 5 | Adversarial Validator | GPT-4o | Stress-tests claims, assigns confidence scores |
| 6 | Master Synthesizer | GPT-4o | Final answer with confidence and reasoning trace |

### Forge Intelligence

Code generation and software engineering pipeline. Stub — coming in a future release.

## Specialist Chat Agents

| Specialist | Provider | Model | Purpose |
|-----------|----------|-------|----------|
| Financial Analyst | Anthropic | Claude Sonnet 4.5 | Market analysis, financial modeling |
| Research Assistant | OpenAI | GPT-4o | Research synthesis, data analysis |
| Code Reviewer | Anthropic | Claude Opus 4.6 | Code review, architecture guidance |
| Legal Quick Consult | xAI | Grok | Legal research, regulatory questions |

## Swarm Mainframe Integration

Dashboard for the Calculus Swarm — a 20-agent caste system running on dedicated GPU infrastructure. Features:

- VM health monitoring (uptime, environment, version)
- Caste system visualization (10 Zerg-inspired castes)
- Skill registry browser (81 skill categories)
- Multi-mode session launcher (round_table, review_chain, specialist, debate)
- Matrix rain animated background
- Password-protected access
- **Calculus Crypto Engine (CCE)** — 8 REST endpoints at `/api/v1/crypto/` for token generation, on-chain analytics, campaign management, compliance checking (Howey test), treasury operations, and liquidity deployment. Powered by HYDRA_CRYPTO and HYDRA_DEFI agent castes with 18 specialized algorithms

## LeadOps / Permit Intelligence

Natural language permit search system for commercial real estate lead generation. Includes analytics dashboards, filter-based search, and export functionality.

## Knowledge Distillation

Captures all conversation turns (specialist, direct chat, pipeline) into a training dataset for fine-tuning local models. Features:

- Automatic conversation turn logging (fire-and-forget async)
- Export to Alpaca JSONL format for Llama fine-tuning
- Readiness checks (recommended 5000+ turns)
- Per-provider and per-source breakdowns

## Training Data Management

Browse, score, and export training data collected from pipeline runs. Quality feedback system with 0.0–1.0 scoring and labels (good/bad/needs_edit). Export in ChatML or Alpaca format.

## Real-Time Streaming

- **Pipelines**: WebSocket streaming with per-agent `agent_start`, `agent_complete`, and `complete` events
- **Chat**: SSE streaming across all providers with token counting

## Quick Start

```bash
cp .env.example .env
# Add API keys (see Environment Variables below)
docker compose -f docker-compose.v2.yml up --build
```

Frontend: http://localhost:3000
Backend API: http://localhost:8000
API docs: http://localhost:8000/docs

## Environment Variables

```env
DB_USER=portal
DB_PASSWORD=<your-db-password>
JWT_SECRET=<your-jwt-secret>
JWT_SECRET_KEY=<your-jwt-secret-key>
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
OPENAI_API_KEY=<your-openai-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
GOOGLE_API_KEY=<your-google-api-key>
XAI_API_KEY=<your-xai-api-key>
GROQ_API_KEY=<your-groq-api-key>
DEEPSEEK_API_KEY=<your-deepseek-api-key>
MISTRAL_API_KEY=<your-mistral-api-key>
COURTLISTENER_API_KEY=<your-courtlistener-api-key>
OLLAMA_HOST=http://<ollama-gpu-ip>:11434
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Vite 7, Tailwind CSS |
| Backend | FastAPI, Python 3.12, Pydantic v2 |
| Database | PostgreSQL 16 (SQLModel ORM) |
| LLM Providers | OpenAI, Anthropic, Google, xAI, DeepSeek, Mistral, Groq, Ollama |
| Local Inference | Ollama on NVIDIA L4 24GB GPU |
| Pipeline Orchestration | CrewAI + LiteLLM (token tracking) |
| Real-Time | WebSocket (pipeline progress), SSE (chat streaming) |
| Infrastructure | Docker Compose, nginx, GCP Compute Engine |
| Testing | pytest (backend), Playwright (E2E) |

## Project Structure

```
backend/
  ├── pipelines/
  │   ├── base_pipeline.py          # Abstract pipeline interface
  │   ├── crew_pipeline.py          # CrewAI wrapper with per-agent callbacks
  │   ├── lex_intelligence.py       # 6-agent legal pipeline
  │   ├── calculus_intelligence.py  # 6-agent reasoning pipeline
  │   └── registry.py              # Pipeline registry
  ├── routes/
  │   ├── chat.py                   # Specialist SSE chat streaming
  │   ├── direct_chat.py            # Multi-model direct chat + model catalog
  │   ├── conversations.py          # Conversation history CRUD
  │   ├── pipelines.py              # Async execution + WebSocket streaming
  │   ├── distillation.py           # Training data export (Alpaca JSONL)
  │   └── training.py               # Training data management + scoring
  ├── providers/
  │   ├── factory.py                # Multi-provider factory (8 providers)
  │   ├── ollama_provider.py        # Local GPU inference via Ollama
  │   └── deepseek_provider.py      # DeepSeek API provider
  ├── models/                       # SQLModel table definitions
  ├── utils/distillation_logger.py  # Fire-and-forget conversation logging
  ├── websockets/                   # WebSocket connection manager
  ├── auth/                         # JWT authentication
  └── config/                       # Settings, pricing, specialist defs
frontend/
  ├── src/
  │   ├── pages/
  │   │   ├── LLMChatPage.tsx       # Intelligence Console (multi-model)
  │   │   ├── ChatPage.tsx          # Specialist chat (Analyst Desks)
  │   │   ├── PipelinesPage.tsx     # Pipeline selection and execution
  │   │   ├── SwarmPage.tsx         # Swarm Mainframe dashboard
  │   │   ├── LeadOpsPage.tsx       # Permit intelligence
  │   │   ├── UsagePage.tsx         # Usage analytics + distillation stats
  │   │   └── SettingsPage.tsx      # Provider & specialist configuration
  │   ├── hooks/
  │   │   ├── usePipeline.ts        # WebSocket-first pipeline hook
  │   │   └── useDirectChat.ts      # Multi-provider chat hook
  │   ├── components/               # Chat, pipeline, usage, leadops UI
  │   └── api/client.ts             # API client with JWT + WebSocket
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/login | Authenticate with email |
| GET | /specialists/ | List all specialists |
| POST | /chat/stream | Stream specialist chat (SSE) |
| GET | /chat/direct/models | Multi-provider model catalog |
| POST | /chat/direct/stream | Stream direct chat (SSE) |
| GET | /conversations/ | List saved conversations |
| GET | /conversations/{uuid}/messages | Load conversation |
| GET | /api/v2/pipelines/list | List available pipelines |
| POST | /api/v2/pipelines/run | Start pipeline (async) |
| WS | /api/v2/pipelines/ws/{id} | Real-time pipeline progress |
| GET | /distillation/stats | Distillation turn statistics |
| POST | /distillation/export | Export training data (Alpaca JSONL) |
| GET | /training/ | Browse training data |
| GET | /usage/ | Usage logs |
| GET | /health | Health check |

## GCP Infrastructure

Production runs on 4 VMs in `us-east1-b`:

| VM | Role | Key Ports |
|----|------|----------|
| fc-ai-portal | AI Portal (frontend + backend + PostgreSQL) | 3000, 8000 |
| swarm-mainframe | Swarm API (20-agent orchestrator + CCE crypto engine) | 8080 |
| swarm-gpu | Triton Inference Server + Ollama GPU inference (NVIDIA L4 24GB), live model routing (Phase 36) | 8000, 11434 |
| calculus-web | Calculus Research website + chatbot | 80 |

## Token Tracking

All pipeline LLMs route through LiteLLM for automatic token counting. Per-agent token usage and costs are tracked via `CrewOutput.token_usage` and proportionally allocated across agents. Multi-model cost efficiency is a design priority — Gemini handles high-volume tasks at ~94% cost reduction vs GPT-4o equivalent.

## Security

Domain-restricted JWT authentication, token-bucket rate limiting (60 req/hour), no persistent storage of raw chat content beyond conversation history. All token usage and costs logged to PostgreSQL.

---

## Shapeshifter Architecture — Three-Layer Model

This repository is part of the **Shapeshifter Orchestration Model**, a three-layer architecture for adaptive multi-agent workflows, distributed execution, and compression-aware model routing.

```
Adaptive Layer        → Shapeshifter (system-wide orchestration model)
Control Plane         → super-duper-spork + Orchestra + AI-PORTAL
Execution Plane       → Triton + BUNNY + distributed workers
```

### Role of `AI-PORTAL`

**Layer:** Control Plane / Interface

AI-PORTAL is the **system interface and telemetry hub** spanning the Control Plane and Adaptive Layer.

Responsibilities within the Shapeshifter architecture:

- authenticated user sessions and Swarm Mainframe UI
- Blueprint Editor for visual Orchestra workflow design
- model registry and experiment tracking
- telemetry dashboards and performance analytics
- feeding runtime metrics into ProbFlow for adaptive routing

### Repository Responsibility Matrix

| Layer     | Component        | Repository          | Role                            |
| --------- | ---------------- | ------------------- | ------------------------------- |
| Adaptive  | Routing & Policy | `ProbFlow`          | uncertainty scoring and routing |
| Control   | Workflow DSL     | `Orchestra`         | task graph definition           |
| Control   | Swarm Runtime    | `super-duper-spork` | scheduling, orchestration, live model routing, CCE crypto engine |
| Execution | Model Runtime    | `Triton`            | AI inference and compression    |
| Execution | Worker Runtime   | `BUNNY`             | distributed execution           |
| Interface | UI & Telemetry   | `AI-PORTAL`         | monitoring and user interaction |

### Execution Lifecycle

```
Task Input → Task Classification → Workflow Selection → Task Graph Compilation
    → Worker Dispatch → Model Execution → Validation → Result Synthesis
```

### Telemetry Feedback Loop

```
Triton runtime metrics → AI-PORTAL dashboards → ProbFlow routing models → Shapeshifter policy updates
```

### Goals & Roadmap

See the [Orchestra README](https://github.com/financecommander/Orchestra#architecture-overview-shapeshifter-orchestration-model) for the full architecture specification, goals, and 7-phase roadmap.

> **Engineering principle:** Use the smallest reliable model and workflow capable of completing the task safely.

## Competitive Projection: System-Level Intelligence

The Shapeshifter architecture competes with frontier LLM systems on **system-level capability**, not single-model capability.

**AI-PORTAL role:** Control Plane / Interface — System Interface and Telemetry Hub

AI-PORTAL provides the observability layer that makes system-level competition possible. Telemetry dashboards, model registry, and Blueprint Editor give operators visibility into the orchestration that frontier LLMs cannot offer as monolithic black boxes.

### System Benchmark Matrix

| Category | Frontier LLM | Shapeshifter Projection |
|---|---|---|
| Coding | very strong | equal or better |
| Large repo analysis | weak | stronger |
| Structured reasoning | strong | equal |
| Operational automation | weak | stronger |
| Research synthesis | strong | equal |
| Cost efficiency | weak | stronger |
| Scalability | limited | far stronger |

### Advantage Mechanisms

| Mechanism | Frontier LLM | Shapeshifter |
|---|---|---|
| Reasoning | sequential | parallel workers |
| Task decomposition | single-pass | explicit planner |
| Validation | self-consistency | layered (static → tests → review → human) |
| Compute | massive GPUs | compressed + ternary + edge workers |

### Simulation Projection

| Metric | Frontier | Shapeshifter |
|---|---|---|
| Reasoning depth | 95 | 85 |
| Parallel execution | 30 | 95 |
| Validation reliability | 60 | 90 |
| Cost efficiency | 40 | 90 |
| Scalability | 35 | 95 |

Frontier models win on deep reasoning. Shapeshifter wins on system-level capability.

> **Shapeshifter is not a model competitor. It is an orchestration architecture that multiplies model capability.**

See the [Orchestra README](https://github.com/financecommander/Orchestra#competitive-projection-system-level-intelligence) for the full competitive projection, benchmark categories, demonstration strategy, and long-term advantage analysis.



---

## License

Proprietary — Calculus Holdings LLC. All rights reserved.

---

## BUNNY Worker Telemetry Contract

> Sourced from the approved **BUNNY Rust Agent Architecture & Sandbox Design** blueprint.

`AI-PORTAL` is the telemetry sink and model registry for all `BUNNY` workers. Every inference a worker performs emits a structured telemetry event that AI-PORTAL stores, aggregates, and exposes on dashboards.

### Per-Inference Telemetry Event (BUNNY → AI-PORTAL)

```json
{
  "worker_id": "bunny-worker-abc123",
  "task_id": "uuid-...",
  "model": "threat_classifier",
  "inference_latency_ms": 1.2,
  "confidence": 0.94,
  "label": "malicious",
  "hardware": "x86_64-linux / A100",
  "sandbox_tier": "firecracker",
  "memory_peak_mb": 48,
  "status": "Success",
  "timestamp": "2026-03-07T12:00:00Z"
}
```

### `ExecutionVerdict` Fields AI-PORTAL Tracks

| Field | Dashboard Use |
|---|---|
| `confidence` | Model accuracy trending, routing quality |
| `hardware_cost.gpu_ms` | Per-model GPU cost breakdown |
| `hardware_cost.memory_peak_mb` | Memory regression detection |
| `duration_ms` | Latency SLA monitoring |
| `status` | Worker health, error rate alerting |
| `sandbox_tier` | Wasm vs MicroVM ratio per task type |

### Worker Fleet View

AI-PORTAL aggregates the capability manifests broadcast by all connected workers:

```json
{
  "worker_id": "bunny-worker-abc123",
  "hardware": { "gpu": "A100", "vram_gb": 40 },
  "sandbox_tiers": ["wasm", "firecracker"],
  "triton_models": ["threat_classifier", "packet_filter"],
  "status": "active",
  "last_heartbeat": "2026-03-07T12:00:05Z"
}
```

This feeds the **Worker Fleet** dashboard and informs `ProbFlow` routing weight updates.

### Model Registry Integration

When Triton publishes a new `.triton` artifact, AI-PORTAL registers it with `model_metadata.json`. BUNNY workers poll AI-PORTAL on startup to discover available models matching their hardware targets.
