# FinanceCommander AI Portal — Development Model Summary

## For the Software Development Team | February 17, 2026

---

## What We're Building

The AI Intelligence Portal v2.0 is a multi-agent platform that lets FinanceCommander employees interact with AI in two modes:

1. **Single-Specialist Chat** — Pick a pre-configured AI specialist (Financial Analyst, Code Reviewer, Legal Quick Consult, etc.) and chat with it. Each specialist is backed by a specific LLM (Claude, GPT, Grok, Gemini) with a tuned system prompt.

2. **Multi-Agent Intelligence Pipelines** — Run complex multi-step research across multiple AI models simultaneously. The flagship is **Lex Intelligence Ultimate**, a 6-agent legal research pipeline that uses 4 different LLMs, cross-validates findings, and produces a structured legal memo with confidence ratings.

---

## Tech Stack

**Backend:** FastAPI (Python 3.12) — async-first, type-hinted
**Frontend:** React 19 + TypeScript + Tailwind (coming next)
**Database:** SQLite (dev) / PostgreSQL (prod) via SQLModel ORM
**Auth:** JWT with domain-restricted email validation
**Pipeline Engine:** CrewAI with LangChain provider wrappers
**Real-time:** WebSocket streaming for pipeline progress
**Providers:** OpenAI, Anthropic, Google Gemini, xAI (Grok)

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              React Frontend                  │
│   (Sidebar → Specialists / Pipelines)        │
└──────────────┬──────────────────┬────────────┘
               │ REST/SSE         │ WebSocket
┌──────────────▼──────────────────▼────────────┐
│             FastAPI Backend                    │
├───────────────────────────────────────────────┤
│  /auth/login          JWT domain validation    │
│  /specialists/        CRUD for AI configs      │
│  /chat/send           Single-model chat        │
│  /chat/stream         SSE streaming chat       │
│  /api/v2/pipelines/   Multi-agent execution    │
│  /usage/logs          Cost & token tracking    │
├───────────────────────────────────────────────┤
│  Provider Layer    │  Pipeline Engine           │
│  ┌──────────────┐  │  ┌───────────────────┐    │
│  │ OpenAI       │  │  │ CrewAI Wrapper     │    │
│  │ Anthropic    │  │  │ ProgressCallback   │    │
│  │ Google       │  │  │ Token Estimator    │    │
│  │ Grok (xAI)   │  │  │ WebSocket Events   │    │
│  └──────────────┘  │  └───────────────────┘    │
├───────────────────────────────────────────────┤
│  SQLite/PostgreSQL  │  Rate Limiter (60/hr)    │
└───────────────────────────────────────────────┘
```

---

## Backend Directory Structure

```
backend/
├── main.py                    # FastAPI app, middleware, route registration
├── config/
│   ├── settings.py            # Environment-driven config (Pydantic)
│   ├── pricing.py             # Per-model token pricing table
│   └── specialists.json       # Default specialist configurations
├── auth/
│   ├── jwt_handler.py         # JWT create/decode
│   └── authenticator.py       # FastAPI Depends() for protected routes
├── providers/
│   ├── base.py                # BaseProvider abstract class
│   ├── openai_provider.py     # OpenAI + Grok (same API, different base_url)
│   ├── anthropic_provider.py  # Claude models
│   ├── google_provider.py     # Gemini models
│   └── factory.py             # get_provider("anthropic") → AnthropicProvider
├── specialists/
│   └── manager.py             # CRUD for specialist configs (JSON-backed)
├── pipelines/
│   ├── base_pipeline.py       # BasePipeline, PipelineResult dataclasses
│   ├── crew_pipeline.py       # CrewAI wrapper with progress callbacks (438 lines)
│   ├── lex_intelligence.py    # 6-agent legal research pipeline (308 lines)
│   ├── calculus_intelligence.py  # Stub — general reasoning (future)
│   ├── forge_intelligence.py  # Stub — coding pipeline (future)
│   └── registry.py            # Pipeline name → instance lookup
├── routes/
│   ├── auth.py                # POST /auth/login
│   ├── chat.py                # POST /chat/send, POST /chat/stream
│   ├── specialists.py         # GET/POST/PUT/DELETE /specialists/
│   ├── pipelines.py           # GET/POST /api/v2/pipelines/, WS streaming
│   └── usage.py               # GET /usage/logs, GET /usage/pipelines
├── websockets/
│   └── ws_manager.py          # WebSocket connection manager for pipeline progress
├── models/
│   └── __init__.py            # UsageLog, PipelineRun (SQLModel ORM)
├── database/
│   └── __init__.py            # Engine, init_db(), get_session()
├── errors/
│   └── exceptions.py          # PortalError hierarchy (auth, provider, pipeline, rate limit)
├── middleware/
│   └── rate_limiter.py        # Token bucket rate limiter (60 req/hr per user)
├── utils/
│   └── token_estimator.py     # Token counting + cost calculation
└── tests/
    ├── test_registry.py
    ├── test_token_estimator.py
    └── test_ws_manager.py
```

---

## Key Design Decisions

### Provider Abstraction
Every LLM provider implements `BaseProvider` with `send_message()` and `stream_message()`. Responses are normalized into `ProviderResponse` regardless of provider. The factory pattern (`get_provider("anthropic")`) means routes never import provider-specific code.

### Specialist System
Specialists are JSON-configured AI personas. Each defines a provider, model, temperature, and system prompt. CRUD operations let users create custom specialists at runtime. This replaces hardcoded model selection.

### Pipeline Engine
CrewAI orchestrates multi-agent workflows. The `ProgressCallback` hooks into LangChain's callback system to track per-agent token usage and cost. Progress streams to the frontend via WebSocket in real-time.

### Token Estimation & Cost Tracking
Every interaction (chat or pipeline) calculates cost using the pricing table. Usage is logged to PostgreSQL with token counts, cost, latency, and provider metadata. This gives full visibility into AI spend.

### Model String Fallbacks
The original spec used unreleased model identifiers. Copilot applied verified fallbacks:
- `grok-4-1-fast-reasoning` → `grok-beta`
- `gpt-5.3-codex` → `gpt-4o`
- `gemini-3-pro` → `gemini-2.0-flash-exp`
- `claude-opus-4-6` → `claude-opus-4-20250514`

All marked with `# TODO: verify model string` for future updates.

---

## Development Workflow

We use a **Poly-Agent Orchestration** approach:

| Tool | Role | Best For |
|------|------|----------|
| Claude Opus (this chat) | Architecture, directives, code review | Complex design decisions, security-critical code |
| GitHub Copilot Agent | Code generation from directives | New files, new modules, greenfield work |
| Codespace Copilot Chat | Implementation, debugging, testing | Fixes, refactoring, anything needing terminal access |

### Directive Flow
1. Claude Opus generates a detailed directive document
2. Directive is tagged 🤖 AGENT or 💻 CODESPACE based on the task
3. Developer submits directive to the appropriate tool
4. PR is reviewed and merged into `develop`
5. Claude Opus reviews results and generates next directive

### Branch Strategy
- `main` — stable releases only
- `develop` — active development (current: 48+ commits)
- `copilot/*` — auto-created by Copilot Agent (merged into develop, then deleted)

---

## What's Complete

- FastAPI backend with all routes functional
- JWT authentication with domain restriction
- 4 LLM providers (OpenAI, Anthropic, Google, Grok)
- 4 default specialists with CRUD
- Chat send/stream with SSE
- Lex Intelligence Ultimate (6-agent legal pipeline)
- Pipeline stubs for Calculus and Forge Intelligence
- WebSocket streaming for pipeline progress
- Token estimation and cost tracking
- Rate limiting (60 requests/hour per user)
- Error hierarchy with global exception handling
- 76+ tests passing

## What's Next

- React frontend (scaffold, auth flow, chat view, pipeline view)
- Docker Compose for local development
- Integration testing (frontend ↔ backend)
- Model string verification against live APIs
- v2.0.0 release and deploy

---

## Running Locally

```bash
# Clone and setup
git clone git@github.com:financecommander/AI-PORTAL.git
cd AI-PORTAL
git checkout develop

# Install dependencies
pip install -r requirements.txt

# Copy env template
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start backend
cd backend
uvicorn backend.main:app --reload --port 8000

# API docs at http://localhost:8000/docs
# Health check at http://localhost:8000/health
```

---

*Document generated: February 17, 2026*
*Project Lead: Sean Grady, CEO*
