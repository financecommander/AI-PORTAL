# CALCULUS LABS AI PORTAL v2.1

Private multi-LLM intelligence platform for legal, financial, and deep reasoning workflows.

Built for Calculus Holdings — February 2026.

## Architecture

```
┌──────────────────────────────────────────────────┐
│               React 19 Frontend                   │
│  Auth │ Chat (SSE) │ Pipelines (WS) │ Usage      │
├──────────────────────────────────────────────────┤
│                 nginx reverse proxy               │
├──────────────────────────────────────────────────┤
│               FastAPI Backend                     │
│  JWT Auth │ Specialists │ Pipelines │ Usage       │
├──────┬───────┬────────┬──────┬───────────────────┤
│GPT-4o│ Grok  │ Gemini │Claude│  CrewAI Pipelines │
├──────┴───────┴────────┴──────┴───────────────────┤
│               PostgreSQL 16                       │
└──────────────────────────────────────────────────┘
```

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

6-agent heterogeneous deep reasoning pipeline. Designed to outperform single-model systems on complex, novel, and multi-domain problems by routing through three different model families and cross-validating their outputs.

| # | Agent | Model | Role |
|---|-------|-------|------|
| 1 | Query Decomposer & Router | GPT-4o | Classifies complexity, breaks into subtasks |
| 2 | Analytical Reasoner | GPT-4o | Structured step-by-step logical reasoning |
| 3 | Creative & Lateral Reasoner | Grok 3 Mini | Alternative perspectives, challenges assumptions |
| 4 | Deep Context Analyst | Gemini 2.5 Flash | Synthesizes agreement/disagreement across paths |
| 5 | Adversarial Validator | GPT-4o | Stress-tests claims, assigns confidence scores |
| 6 | Master Synthesizer | GPT-4o | Final answer with confidence and reasoning trace |

The core advantage: when GPT-4o and Grok independently reach the same conclusion, confidence is high. When they diverge, the validator digs in. A single model family cannot do this.

### Forge Intelligence

Code generation and software engineering pipeline. Stub — coming in a future release.

## Specialist Chat Agents

| Specialist | Provider | Model | Purpose |
|-----------|----------|-------|---------|
| Financial Analyst | Anthropic | Claude Sonnet 4.5 | Market analysis, financial modeling |
| Research Assistant | OpenAI | GPT-4o | Research synthesis, data analysis |
| Code Reviewer | Anthropic | Claude Opus 4.6 | Code review, architecture guidance |
| Legal Quick Consult | xAI | Grok | Legal research, regulatory questions |

## Real-Time Pipeline Streaming

Pipelines stream progress via WebSocket. The frontend shows per-agent status as each agent starts and completes, with token counts and cost tracking populated on completion.

The backend executes pipelines asynchronously (POST returns immediately with a pipeline ID), and the frontend connects via WebSocket to receive `agent_start`, `agent_complete`, and `complete` events in real time.

## Quick Start

```bash
cp .env.example .env
# Add API keys: OPENAI_API_KEY, XAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY
docker compose -f docker-compose.v2.yml up --build
```

Frontend: http://localhost:3000
Backend API: http://localhost:8000
API docs: http://localhost:8000/docs

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Vite 7, Tailwind CSS |
| Backend | FastAPI, Python 3.12, Pydantic v2 |
| Database | PostgreSQL 16 |
| LLM Providers | OpenAI GPT-4o, xAI Grok 3 Mini, Google Gemini 2.5 Flash, Anthropic Claude |
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
  │   ├── calculus_intelligence.py   # 6-agent reasoning pipeline
  │   ├── forge_intelligence.py     # Stub for future code gen pipeline
  │   └── registry.py              # Pipeline registry
  ├── routes/
  │   ├── pipelines.py             # Async execution + WebSocket streaming
  │   └── chat.py                  # SSE chat streaming
  ├── providers/                   # LLM provider abstraction
  ├── websockets/                  # WebSocket connection manager
  ├── auth/                        # JWT authentication
  └── config/                      # Settings, pricing, specialist defs
frontend/
  ├── src/
  │   ├── hooks/usePipeline.ts     # WebSocket-first pipeline hook
  │   ├── components/pipeline/     # Progress cards, agent status
  │   ├── pages/PipelinesPage.tsx  # Pipeline selection and execution
  │   └── api/client.ts            # API client with JWT + WebSocket
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/login | Authenticate with email |
| GET | /specialists/ | List all specialists |
| POST | /chat/stream | Stream chat response (SSE) |
| GET | /api/v2/pipelines/list | List available pipelines |
| POST | /api/v2/pipelines/run | Start pipeline (returns immediately) |
| WS | /api/v2/pipelines/ws/{id} | Real-time pipeline progress |
| GET | /usage/ | Usage logs |
| GET | /health | Health check |

## Token Tracking

All pipeline LLMs use `crewai.LLM` which routes through LiteLLM for automatic token counting. Per-agent token usage and costs are tracked via `CrewOutput.token_usage` and proportionally allocated across agents. Multi-model cost efficiency is a design priority — Gemini handles high-volume tasks at ~94% cost reduction vs GPT-4o equivalent.

## Security

Domain-restricted JWT authentication, token-bucket rate limiting (60 req/hour), no persistent storage of chat content. All token usage and costs logged to PostgreSQL.

## Deployment

Production instance runs on GCP Compute Engine (us-east1-b) with Docker Compose. Backend and frontend are separate containers behind nginx.

```bash
# On VM
cd ~/AI-PORTAL && git pull origin main
docker compose -f docker-compose.v2.yml build --no-cache backend
docker compose -f docker-compose.v2.yml up -d
```

## License

Proprietary — Calculus Holdings LLC. All rights reserved.