# FinanceCommander AI Intelligence Portal v2.0

> Private AI-powered legal and financial intelligence platform for the Calculus Holdings team.

## Architecture

```
┌─────────────────────────────────────────────┐
│              React 19 Frontend               │
│  Auth │ Chat (SSE) │ Pipeline (WS) │ Usage  │
├─────────────────────────────────────────────┤
│                nginx reverse proxy           │
├─────────────────────────────────────────────┤
│              FastAPI Backend                  │
│  JWT Auth │ Specialists │ Pipelines │ Usage  │
├──────┬──────┬──────┬──────┬─────────────────┤
│Claude│GPT-4o│Gemini│ Grok │  Lex Pipeline   │
├──────┴──────┴──────┴──────┴─────────────────┤
│              PostgreSQL 16                    │
└─────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API keys for at least one LLM provider

### Run with Docker
```bash
cp .env.example .env
# Edit .env with your API keys and secrets
docker compose -f docker-compose.v2.yml up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Run Locally (Development)
```bash
# Backend
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Features

### Specialist Chat Agents
| Specialist | Provider | Model | Purpose |
|-----------|----------|-------|---------|
| Financial Analyst | Anthropic | Claude Sonnet 4.5 | Market analysis, financial modeling |
| Research Assistant | OpenAI | GPT-4o | Research synthesis, data analysis |
| Code Reviewer | Anthropic | Claude Opus 4.6 | Code review, architecture guidance |
| Legal Quick Consult | xAI | Grok | Legal research, regulatory questions |

### Lex Intelligence Pipeline
6-agent multi-LLM pipeline for comprehensive legal/financial analysis:
1. Lead Researcher (GPT-4o) — primary research
2. Contrarian Analyst (Claude Sonnet) — counter-arguments
3. Regulatory Scanner (Gemini 2.0 Flash) — compliance check
4. Quantitative Modeler (GPT-4o) — numerical analysis
5. Convergence Synthesizer (Claude Opus) — synthesis
6. Final Editor (Claude Opus) — publication-quality output

Real-time agent progress via WebSocket streaming.

### Security
- JWT authentication with domain validation (@financecommander.com)
- Token-bucket rate limiting (60 req/hour)
- No data persistence of chat content (privacy-first)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite 7, Tailwind CSS |
| Backend | FastAPI, Python 3.12, Pydantic v2 |
| Database | PostgreSQL 16 |
| LLM Providers | Anthropic, OpenAI, Google, xAI |
| Pipeline | CrewAI (agent orchestration) |
| Infrastructure | Docker Compose, nginx |
| Testing | pytest (backend), Playwright (E2E) |

## Project Structure
```
├── backend/           # FastAPI application
│   ├── auth/         # JWT authentication
│   ├── config/       # Settings, pricing, specialist definitions
│   ├── errors/       # Custom exception hierarchy
│   ├── middleware/    # Rate limiter
│   ├── models/       # Pydantic models
│   ├── pipelines/    # Lex Intelligence, CrewAI wrapper
│   ├── providers/    # LLM provider abstraction layer
│   ├── routes/       # API endpoints
│   ├── specialists/  # Specialist manager
│   ├── tests/        # Backend test suite
│   ├── utils/        # Token estimator
│   └── websockets/   # WebSocket connection manager
├── frontend/          # React application
│   ├── src/
│   │   ├── api/          # API client with JWT injection
│   │   ├── components/   # Chat, Pipeline, Usage components
│   │   ├── contexts/     # Auth context
│   │   ├── hooks/        # useChat, usePipeline
│   │   ├── pages/        # Route pages
│   │   └── types/        # TypeScript interfaces
│   └── e2e/              # Playwright E2E tests
├── docs/              # Documentation
│   ├── agents/       # Agent READMEs (specialists, coding, pipeline)
│   ├── directives/   # Copilot Agent execution directives
│   └── planning/     # v2.2 planning spec, team summary
├── docker-compose.v2.yml  # Production stack
├── Dockerfile.backend
└── frontend/Dockerfile.frontend
```

## Testing

```bash
# Backend unit tests
cd backend && python -m pytest tests/ -v

# Frontend E2E tests
cd frontend && npx playwright test

# Frontend build check
cd frontend && npm run build
```

## API Endpoints

| Method | Path | Description |
|--------|------|------------|
| POST | /auth/login | Authenticate with email |
| GET | /auth/verify | Verify JWT token |
| GET | /specialists/ | List all specialists |
| GET | /specialists/{id} | Get specialist details |
| POST | /chat/send | Send chat message |
| POST | /chat/stream | Stream chat response (SSE) |
| GET | /api/v2/pipelines/ | List available pipelines |
| POST | /api/v2/pipelines/run | Execute pipeline |
| WS | /api/v2/pipelines/ws/{run_id} | Pipeline progress stream |
| GET | /usage/ | Get usage logs |
| GET | /health | Health check |

## Roadmap

| Version | Target | Focus |
|---------|--------|-------|
| v2.0.0 | Feb 2026 | ✅ Full-stack portal (current) |
| v2.1.0 | May 2026 | Team deployment, RBAC, model upgrades |
| v2.2.0 | Oct 2026 | Multi-jurisdiction, governance agents |
| v2.3.0 | Mar 2027 | Public SaaS launch |

## Documentation

See [`docs/README.md`](docs/README.md) for full documentation index.

## License

Proprietary — Calculus Holdings LLC. All rights reserved.
- **Providers**: Unified interface for multiple LLM providers
- **Chat Engine**: Conversation orchestration with history management
- **Usage Logger**: Performance and cost tracking

### Security Features

- Email hashing for privacy compliance
- Domain-based access control
- No plaintext secrets in code
- Environment-based configuration

## Setup

### Prerequisites

- Python 3.12+
- API keys for desired providers (OpenAI, Anthropic, Google)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-portal
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Configure Streamlit secrets:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml with your API keys
```

5. Run the application:
```bash
streamlit run app.py
```

## Configuration

### Environment Variables (.env)

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

### Streamlit Secrets

Configure API keys in `.streamlit/secrets.toml`:

```toml
[openai]
api_key = "your_openai_key"

[anthropic]
api_key = "your_anthropic_key"

[google]
api_key = "your_google_key"
```

### Specialists Configuration

Edit `config/specialists.json` to customize AI specialists:

```json
{
  "financial-analyst": {
    "name": "Financial Analyst",
    "system_prompt": "You are a financial analyst...",
    "model": "gpt-4o",
    "provider": "openai",
    "temperature": 0.5
  }
}
```

## Usage

1. Start the application with `streamlit run app.py`
2. Authenticate with a valid domain email
3. Select an AI specialist from the sidebar
4. Start chatting for financial analysis and insights

## Development

### Testing

Run the test suite (248 tests):
```bash
# All tests (excluding live API tests)
python -m pytest tests/ -m "not live" -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Performance benchmarks
python -m pytest tests/performance/ -v
```

### Project Structure

```
├── app.py                    # Main Streamlit application
├── auth/                     # Authentication, session timeout, rate limiter
│   ├── authenticator.py      # Domain auth + session timeout
│   └── rate_limiter.py       # Token-bucket rate limiter
├── chat/                     # Chat engine, logging, search, file handling
│   ├── engine.py             # Conversation orchestration (streaming + sync)
│   ├── file_handler.py       # File upload processing + ChatAttachment
│   ├── logger.py             # CSV usage logging + specialist stats
│   └── search.py             # Conversation history search
├── config/                   # Configuration and settings
│   ├── pricing.py            # Per-model token pricing table
│   ├── settings.py           # App-wide constants
│   └── specialists.json      # Default specialist definitions
├── docs/                     # Documentation
│   ├── ADMIN.md              # Administrator guide
│   ├── ARCHITECTURE.md       # Architecture overview with diagrams
│   ├── DEPLOYMENT.md         # Deployment guide (local, Docker, Cloud)
│   ├── SECURITY.md           # Security checklist
│   └── TECH_DEBT.md          # Technical debt log
├── ledgerscript/             # Domain-specific language
│   └── grammar.py            # LedgerScript DSL grammar parser
├── portal/                   # Core portal types
│   └── errors.py             # Typed exception hierarchy
├── providers/                # LLM provider implementations
│   ├── base.py               # BaseProvider ABC + dataclasses
│   ├── openai_provider.py    # OpenAI + Grok
│   ├── anthropic_provider.py # Anthropic Claude
│   └── google_provider.py    # Google Gemini
├── scripts/                  # Utility scripts
│   └── cost_report.py        # Usage cost report generator
├── specialists/              # AI specialist management
│   └── manager.py            # CRUD + duplication + pinning
├── tests/                    # Test suite (248 tests)
│   ├── conftest.py           # Shared fixtures
│   ├── unit/                 # Fast, isolated unit tests
│   ├── integration/          # Multi-component workflow tests
│   ├── live/                 # Real API tests (require keys)
│   └── performance/          # Benchmarks with time assertions
├── ui/                       # Streamlit UI components
│   ├── chat_view.py          # Chat display, search, file upload, tokens
│   └── sidebar.py            # Specialist selector, CRUD, pinning, stats
├── Dockerfile                # Container image
├── docker-compose.yml        # Docker Compose config
├── pyproject.toml            # Pytest configuration
└── requirements.txt          # Python dependencies
```

## Security

- All user emails are hashed with SHA-256 before logging
- API keys are stored in environment variables and Streamlit secrets
- Domain-based authentication restricts access
- No sensitive data is committed to version control

## License

[Add license information]

## Contributing

[Add contribution guidelines]
