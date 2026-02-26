# Phase 3E — Tests, CI/CD, README, Docker Validation

## Context

You are working on the `financecommander/AI-PORTAL` repo, branch: `develop`.

This is a full-stack AI Intelligence Portal (v2.0.0) with:
- **Backend**: FastAPI (Python 3.12) at `backend/` — JWT auth, 4 LLM providers, specialist CRUD, chat with SSE streaming, Lex Intelligence pipeline with WebSocket streaming, rate limiter, usage logging
- **Frontend**: React 19 + TypeScript + Vite 7 + Tailwind CSS at `frontend/` — auth flow, chat interface, pipeline execution view, usage dashboard, settings page
- **Infrastructure**: `docker-compose.v2.yml` (PostgreSQL 16 + FastAPI + nginx), `Dockerfile.backend`, `frontend/Dockerfile.frontend`, `frontend/nginx.conf`
- **Existing backend tests**: `backend/tests/` (test_registry.py, test_security_fixes.py, test_token_estimator.py, test_ws_manager.py) + `tests/` (legacy v1 tests — unit, integration, performance, live)

## CRITICAL CONSTRAINTS

- **Branch**: Create `feature/phase-3e-tests-ci-readme` from `develop`
- **DO NOT** modify any existing source code in `backend/` or `frontend/src/`
- **DO NOT** install LLM API keys or real credentials — use mocks/fixtures only
- **DO NOT** add `node_modules/`, `__pycache__/`, `.env`, or `dist/` to git
- Commit message: `feat: Phase 3E — E2E tests, backend test expansion, CI/CD, README, Docker validation`
- Open PR to `develop` when complete

---

## SECTION 1: Backend Test Expansion

### Goal
Expand `backend/tests/` to cover routes, auth, providers, pipelines, and middleware. Target: 85%+ coverage on backend package.

### Files to Create

#### `backend/tests/conftest.py`
Shared fixtures for all backend tests:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

# Mock all LLM provider API keys before importing app
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-for-testing-only")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

@pytest.fixture
def client():
    """TestClient for FastAPI app."""
    from backend.main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Valid JWT auth headers for protected routes."""
    from backend.auth.jwt_handler import create_token
    token = create_token({"sub": "test@financecommander.com"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_provider():
    """Mock LLM provider that returns canned responses."""
    provider = AsyncMock()
    provider.chat.return_value = {
        "content": "Mock response",
        "tokens_used": {"prompt": 10, "completion": 20, "total": 30},
        "cost": 0.001,
        "model": "test-model"
    }
    provider.stream_chat = AsyncMock()
    return provider
```

#### `backend/tests/test_auth_routes.py`
Test the `/auth/login` and `/auth/verify` endpoints:
- Valid login with `@financecommander.com` email → 200 + JWT token
- Invalid domain email → 401/403
- Missing email field → 422
- Token verification with valid JWT → 200
- Token verification with expired/invalid JWT → 401
- Token verification with missing Authorization header → 401

#### `backend/tests/test_chat_routes.py`
Test `/chat/send` and `/chat/stream` endpoints:
- Send message with valid auth → 200 + response body with content, tokens, cost
- Send message without auth → 401
- Send message with invalid specialist_id → 404
- Stream endpoint returns SSE content-type
- Mock the provider to avoid real API calls
- Verify usage logging is called after successful chat

#### `backend/tests/test_specialist_routes.py`
Test CRUD at `/specialists/`:
- GET `/specialists/` → 200 + list of specialists
- GET `/specialists/{id}` → 200 + single specialist
- GET `/specialists/{invalid-id}` → 404
- POST `/specialists/` with valid data → 201
- POST `/specialists/` with missing fields → 422
- PUT `/specialists/{id}` → 200
- DELETE `/specialists/{id}` → 200
- All routes require auth → 401 without token

#### `backend/tests/test_usage_routes.py`
Test `/usage/` endpoint:
- GET `/usage/` with auth → 200 + usage logs array
- GET `/usage/` without auth → 401
- Verify response schema has expected fields (timestamp, specialist, tokens, cost, latency)

#### `backend/tests/test_pipeline_routes.py`
Test `/api/v2/pipelines/` endpoints:
- GET `/api/v2/pipelines/` → 200 + list of available pipelines
- POST `/api/v2/pipelines/run` with valid query → 200 (mock CrewAI execution)
- POST `/api/v2/pipelines/run` without auth → 401
- POST `/api/v2/pipelines/run` with empty query → 422
- Mock the pipeline execution to avoid real LLM calls

#### `backend/tests/test_providers_unit.py`
Test provider factory and base provider:
- Factory returns correct provider class for each provider name (anthropic, openai, google, xai)
- Factory raises error for unknown provider
- Base provider abstract methods are defined
- Provider initialization with valid config

#### `backend/tests/test_middleware.py`
Test rate limiter middleware:
- Request within rate limit → passes through
- Request exceeding rate limit → 429 response
- Rate limit resets after window expires
- Different users have independent rate limits

### Test Runner Config

#### `backend/pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
```

Wait — the backend tests are in `backend/tests/`. Create a `backend/pyproject.toml` or add pytest config:

#### `backend/pyproject.toml` (create or append)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
```

---

## SECTION 2: Frontend E2E Tests (Playwright)

### Goal
Create Playwright E2E test suite for the React frontend. Tests run against a mock backend (MSW or static fixtures).

### Setup Files

#### `frontend/package.json` updates
Add to devDependencies:
```json
"@playwright/test": "^1.50.0"
```

Add to scripts:
```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui"
```

#### `frontend/playwright.config.ts`
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
});
```

### Test Files

#### `frontend/e2e/auth.spec.ts`
- Login page renders with email input and submit button
- Entering non-@financecommander.com email shows error
- Entering valid @financecommander.com email redirects to chat page
- Unauthenticated user is redirected to login page
- Logout button clears session and redirects to login

#### `frontend/e2e/chat.spec.ts`
- Chat page renders specialist selector panel
- Clicking a specialist shows chat interface with specialist header
- Typing a message and pressing Enter sends message (mock backend)
- Message bubbles appear for user and assistant messages
- Empty state shows example prompts
- Stop button appears during streaming

#### `frontend/e2e/navigation.spec.ts`
- Sidebar renders with 4 navigation items (Chat, Pipelines, Usage, Settings)
- Clicking each nav item navigates to correct page
- Active nav item is highlighted
- Sidebar shows user email
- Logout button works from any page

#### `frontend/e2e/pipelines.spec.ts`
- Pipelines page shows available pipeline cards
- Clicking a pipeline shows query input
- Submitting a query shows progress indicators
- Back button returns to pipeline selection

#### `frontend/e2e/usage.spec.ts`
- Usage page renders stats cards
- Cost chart displays
- Usage table shows log entries
- Tab switching between chat logs and pipeline runs works

### Mock Setup

#### `frontend/e2e/fixtures/mock-api.ts`
Create a Playwright route handler that intercepts API calls and returns mock data:
- `POST /auth/login` → `{ token: "mock-jwt-token" }`
- `GET /specialists/` → array of 4 specialists matching `backend/config/specialists.json`
- `POST /chat/send` → `{ content: "Mock response", tokens_used: {...}, cost: 0.001 }`
- `GET /api/v2/pipelines/` → array of available pipelines
- `GET /usage/` → array of mock usage logs
- `GET /health` → `{ status: "ok" }`

Use `page.route()` in a shared beforeEach fixture, NOT MSW (to avoid additional dependencies).

---

## SECTION 3: README Overhaul

### Goal
Replace the root `README.md` with a comprehensive v2.0 README.

### File: `README.md` (replace entire contents)

Structure:
```markdown
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
```

IMPORTANT: The README must contain the ASCII architecture diagram, all tables, the project structure tree, and the roadmap. Do not omit any sections.

---

## SECTION 4: CI/CD Pipeline (GitHub Actions)

### Goal
Create GitHub Actions workflows for automated testing and build validation on every push and PR.

### Files to Create

#### `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx
      
      - name: Run backend tests
        env:
          JWT_SECRET: ci-test-secret
          ANTHROPIC_API_KEY: test-key
          OPENAI_API_KEY: test-key
          XAI_API_KEY: test-key
          GOOGLE_API_KEY: test-key
        run: |
          cd backend
          python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
      
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js 22
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Type check
        run: cd frontend && npx tsc -b --noEmit
      
      - name: Lint
        run: cd frontend && npx eslint src/ --max-warnings 0
        continue-on-error: true
      
      - name: Build
        run: cd frontend && npm run build
      
  frontend-e2e:
    runs-on: ubuntu-latest
    needs: frontend-build
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js 22
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Install Playwright browsers
        run: cd frontend && npx playwright install --with-deps chromium
      
      - name: Run E2E tests
        run: cd frontend && npx playwright test --reporter=github
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 7

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build backend image
        run: docker build -f Dockerfile.backend -t fc-portal-backend:test .
      
      - name: Build frontend image
        run: docker build -f frontend/Dockerfile.frontend -t fc-portal-frontend:test frontend/
      
      - name: Verify images
        run: |
          docker images | grep fc-portal
          echo "Backend image size: $(docker image inspect fc-portal-backend:test --format='{{.Size}}' | numfmt --to=iec)"
          echo "Frontend image size: $(docker image inspect fc-portal-frontend:test --format='{{.Size}}' | numfmt --to=iec)"
```

#### `.github/workflows/docker-smoke.yml`
```yaml
name: Docker Smoke Test

on:
  push:
    tags: ['v*']
  workflow_dispatch:

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Create test env
        run: |
          cat > .env << EOF
          DB_USER=portal
          DB_PASSWORD=testpassword123
          JWT_SECRET=smoke-test-secret
          ANTHROPIC_API_KEY=test-key
          OPENAI_API_KEY=test-key
          XAI_API_KEY=test-key
          GOOGLE_API_KEY=test-key
          EOF
      
      - name: Start Docker Compose stack
        run: docker compose -f docker-compose.v2.yml up -d --build
      
      - name: Wait for services
        run: |
          echo "Waiting for PostgreSQL..."
          timeout 60 bash -c 'until docker compose -f docker-compose.v2.yml exec -T db pg_isready -U portal; do sleep 2; done'
          echo "Waiting for backend..."
          timeout 60 bash -c 'until curl -sf http://localhost:8000/health; do sleep 2; done'
          echo "Waiting for frontend..."
          timeout 60 bash -c 'until curl -sf http://localhost:3000; do sleep 2; done'
      
      - name: Verify backend health
        run: |
          STATUS=$(curl -sf http://localhost:8000/health | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
          echo "Backend health: $STATUS"
          [ "$STATUS" = "ok" ] || [ "$STATUS" = "healthy" ] || exit 1
      
      - name: Verify frontend serves
        run: |
          HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" http://localhost:3000)
          echo "Frontend HTTP: $HTTP_CODE"
          [ "$HTTP_CODE" = "200" ] || exit 1
      
      - name: Verify API proxy through frontend
        run: |
          HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" http://localhost:3000/health)
          echo "API proxy HTTP: $HTTP_CODE"
          [ "$HTTP_CODE" = "200" ] || exit 1
      
      - name: Check container logs for errors
        if: always()
        run: |
          echo "=== Backend logs ==="
          docker compose -f docker-compose.v2.yml logs backend --tail=50
          echo "=== Frontend logs ==="
          docker compose -f docker-compose.v2.yml logs frontend --tail=20
      
      - name: Cleanup
        if: always()
        run: docker compose -f docker-compose.v2.yml down -v
```

---

## SECTION 5: Docker Smoke Test Script (Local)

### Goal
A standalone bash script developers can run locally to validate the Docker stack.

### File: `scripts/docker-smoke-test.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "🐳 FinanceCommander AI Portal — Docker Smoke Test"
echo "================================================="

# Create temporary .env if not exists
if [ ! -f .env ]; then
    echo "Creating temporary .env for smoke test..."
    cat > .env << EOF
DB_USER=portal
DB_PASSWORD=smoketest123
JWT_SECRET=smoke-test-secret-key
ANTHROPIC_API_KEY=test-key
OPENAI_API_KEY=test-key
XAI_API_KEY=test-key
GOOGLE_API_KEY=test-key
EOF
    CLEANUP_ENV=true
else
    CLEANUP_ENV=false
fi

cleanup() {
    echo "Cleaning up..."
    docker compose -f docker-compose.v2.yml down -v 2>/dev/null || true
    if [ "$CLEANUP_ENV" = true ]; then
        rm -f .env
    fi
}
trap cleanup EXIT

echo "Building and starting services..."
docker compose -f docker-compose.v2.yml up -d --build

echo "Waiting for PostgreSQL (max 60s)..."
for i in $(seq 1 30); do
    if docker compose -f docker-compose.v2.yml exec -T db pg_isready -U portal -d ai_portal 2>/dev/null; then
        echo "  ✅ PostgreSQL ready"
        break
    fi
    sleep 2
done

echo "Waiting for backend (max 60s)..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "  ✅ Backend healthy"
        break
    fi
    sleep 2
done

echo "Waiting for frontend (max 30s)..."
for i in $(seq 1 15); do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo "  ✅ Frontend serving"
        break
    fi
    sleep 2
done

echo ""
echo "Running health checks..."

# Backend health
HEALTH=$(curl -sf http://localhost:8000/health 2>/dev/null || echo '{"status":"unreachable"}')
echo "  Backend:  $HEALTH"

# Frontend serves HTML
if curl -sf http://localhost:3000 | grep -q "html" 2>/dev/null; then
    echo "  Frontend: ✅ Serving HTML"
else
    echo "  Frontend: ❌ Not serving"
fi

# API proxy
if curl -sf http://localhost:3000/health > /dev/null 2>&1; then
    echo "  API Proxy: ✅ Working"
else
    echo "  API Proxy: ❌ Not proxying"
fi

# Specialists endpoint
SPECIALISTS=$(curl -sf http://localhost:8000/specialists/ 2>/dev/null || echo "unreachable")
echo "  Specialists: $SPECIALISTS" | head -c 200

echo ""
echo "================================================="
echo "🎉 Docker smoke test complete!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
```

Mark executable:
```bash
chmod +x scripts/docker-smoke-test.sh
```

---

## Verification Checklist

Before opening the PR, verify:

1. **Backend tests**: `cd backend && python -m pytest tests/ -v` — all pass
2. **Frontend build**: `cd frontend && npm run build` — succeeds with 0 errors
3. **Playwright config**: `frontend/playwright.config.ts` exists and is valid TypeScript
4. **CI workflow**: `.github/workflows/ci.yml` is valid YAML
5. **Docker smoke workflow**: `.github/workflows/docker-smoke.yml` is valid YAML
6. **Smoke test script**: `scripts/docker-smoke-test.sh` is executable
7. **README**: Root `README.md` contains architecture diagram, feature tables, and project structure
8. **No source changes**: No modifications to existing files in `backend/` source or `frontend/src/`

## Commit & PR

```bash
git add -A
git commit -m "feat: Phase 3E — E2E tests, backend test expansion, CI/CD, README, Docker validation"
```

Open PR to `develop` with title: **Phase 3E: Tests, CI/CD, README, Docker Validation**

PR description:
```
## What
- Backend test expansion (8 new test files, 85%+ coverage target)
- Playwright E2E test suite (5 spec files covering auth, chat, nav, pipelines, usage)
- GitHub Actions CI (backend tests, frontend build, E2E, Docker build)
- Docker smoke test workflow (runs on version tags)
- Local Docker smoke test script
- README overhaul for v2.0

## Why
Production hardening for v2.0.0 release. Automated quality gates for all future PRs.

## Testing
- Backend: `cd backend && python -m pytest tests/ -v`
- Frontend: `cd frontend && npm run build`
- E2E: `cd frontend && npx playwright test`
- Docker: `./scripts/docker-smoke-test.sh`
```
