# Phase 3D: Usage Dashboard, Settings Page, Docker Compose & Production Wiring

**Target branch:** `develop`
**New branch:** `feature/phase-3d-usage-settings-docker`
**PR target:** `develop`
**Scope:** Complete the remaining frontend pages (Usage dashboard with charts, Settings page), create production Docker Compose with frontend + backend + PostgreSQL, and update the Dockerfile for the v2.0 architecture.

---

## CRITICAL CONSTRAINTS

- **DO NOT** modify `api/client.ts`, `types/index.ts`, `AuthContext.tsx`, `Sidebar.tsx`, or `Layout.tsx`
- **DO NOT** modify any files in `backend/` — the API is complete
- **DO NOT** add heavy charting libraries — use simple CSS-based charts (bar charts via div widths, or basic SVG)
- **DO** reuse existing CSS variables from `index.css`
- **DO** use existing types from `types/index.ts` (`UsageLog`)
- **DO** use `api.request()` for all API calls

---

## Backend API Contract (DO NOT MODIFY — build frontend to match)

**Usage logs:**
```
GET /usage/logs?limit=50
Response: { logs: UsageLog[] }
UsageLog: { id, user_hash, timestamp, provider, model, input_tokens, output_tokens, cost_usd, latency_ms, specialist_id? }
```

**Pipeline runs:**
```
GET /usage/pipelines?limit=20
Response: { runs: PipelineRun[] }
```

**Specialists list (for settings display):**
```
GET /specialists/
Response: { specialists: Specialist[] }
```

---

## Files to Create/Modify

### 1. CREATE `frontend/src/components/usage/CostChart.tsx`

Simple bar chart showing daily cost breakdown.

```typescript
interface CostChartProps {
  data: { date: string; cost: number; count: number }[];
}
```

**Requirements:**
- Pure CSS bar chart — NO chart libraries. Each bar is a div with dynamic width/height.
- Horizontal bars, one per day (last 7 days)
- Bar color: var(--blue), background track: var(--navy-light)
- Label left: date (Mon, Tue, etc.), label right: $X.XX
- Max bar width scales to the highest cost day
- Below chart: total row showing sum cost and sum count
- If no data: show "No usage data yet" in muted text

### 2. CREATE `frontend/src/components/usage/UsageTable.tsx`

Table showing recent usage logs.

```typescript
interface UsageTableProps {
  logs: UsageLog[];
}
```

**Requirements:**
- Responsive table, background var(--navy), rounded-xl, overflow-x-auto
- Columns: Time (relative, e.g. "2h ago"), Specialist, Provider, Model, Tokens (in+out), Cost, Latency
- Header row: background var(--navy-dark), text #8899AA, text-xs uppercase
- Data rows: alternating subtle backgrounds (var(--navy) / slightly lighter), text-sm
- Time column: use relative time formatting (write a simple helper — "just now", "5m ago", "2h ago", "yesterday", etc.)
- Cost column: green text for < $0.05, orange for $0.05-$0.50, red for > $0.50
- Tokens column: format as "1.2k" for thousands
- Empty state: "No usage logs yet — start chatting to see your usage here"
- Max 50 rows displayed

### 3. CREATE `frontend/src/components/usage/StatsCards.tsx`

Summary stat cards at top of usage page.

```typescript
interface StatsCardsProps {
  logs: UsageLog[];
}
```

**Requirements:**
- Row of 4 cards, equal width, background var(--navy), rounded-xl, padding 20px
- Card 1: "Total Cost" — sum of all cost_usd, large text var(--blue), dollar formatted
- Card 2: "Total Tokens" — sum of input+output tokens, formatted with k/M suffix
- Card 3: "Avg Latency" — average latency_ms, formatted as seconds (1.2s)
- Card 4: "Total Queries" — count of logs
- Each card: label in muted text-xs above, value in text-2xl font-bold below
- Calculate all stats from the logs array passed in (client-side aggregation)

### 4. MODIFY `frontend/src/pages/UsagePage.tsx`

Replace stub with full usage dashboard.

**Requirements:**
- On mount: fetch `GET /usage/logs?limit=50` and `GET /usage/pipelines?limit=20`
- Layout:
```
┌──────────────────────────────────────────┐
│ "Usage & Costs" header                    │
├──────────────────────────────────────────┤
│ [StatsCards — 4 summary cards in a row]   │
├──────────────────────────────────────────┤
│ [CostChart — last 7 days bar chart]       │
├──────────────────────────────────────────┤
│ Two tabs: "Chat Logs" | "Pipeline Runs"   │
│ [UsageTable — showing selected tab data]  │
└──────────────────────────────────────────┘
```
- Tabs: simple toggle buttons, active tab has var(--blue) bottom border + white text, inactive is muted
- Pipeline runs tab: reuse UsageTable but adapt columns (pipeline_name, query preview, status, total_cost, duration, created_at)
- Loading state: skeleton placeholders (pulsing var(--navy-light) blocks) while data loads
- Error state: retry button if fetch fails

### 5. MODIFY `frontend/src/pages/SettingsPage.tsx`

Replace stub with settings display page.

**Requirements:**
- Layout:
```
┌──────────────────────────────────────────┐
│ "Settings" header                         │
├──────────────────────────────────────────┤
│ Portal Info card                          │
│  Version: 2.0.0                           │
│  Backend: FastAPI + Python 3.12           │
│  Frontend: React 19 + TypeScript          │
│  LLM Providers: 4 (Anthropic, OpenAI,    │
│    xAI, Google)                           │
├──────────────────────────────────────────┤
│ Configured Specialists                    │
│  [list of specialists with provider/model]│
├──────────────────────────────────────────┤
│ Available Pipelines                       │
│  [list of pipelines with agent count]     │
├──────────────────────────────────────────┤
│ Your Session                              │
│  Token: fc_***...*** (masked)             │
│  [Sign Out button]                        │
└──────────────────────────────────────────┘
```
- Fetch specialists from `GET /specialists/` and pipelines from `GET /api/v2/pipelines/list`
- Each section is a card (background var(--navy), rounded-xl, padding 20px, margin-bottom 16px)
- Specialists displayed as rows with name, provider pill, model pill, temperature badge
- Pipelines displayed as rows with name, agent count badge, description
- Session section: show masked JWT token (first 6 + last 4 chars), sign out button calls `logout()` from AuthContext
- All read-only — no edit forms in v2.0 (note: "Specialist configuration available in v2.1")

### 6. CREATE `docker-compose.v2.yml` (in repo root)

Production Docker Compose for v2.0 stack.

```yaml
version: '3.8'

services:
  # PostgreSQL database
  db:
    image: postgres:16-alpine
    container_name: fc-portal-db
    environment:
      POSTGRES_DB: ai_portal
      POSTGRES_USER: ${DB_USER:-portal}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB_PASSWORD required}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U portal -d ai_portal"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # FastAPI backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: fc-portal-backend
    environment:
      DATABASE_URL: postgresql://${DB_USER:-portal}:${DB_PASSWORD}@db:5432/ai_portal
      JWT_SECRET: ${JWT_SECRET:?JWT_SECRET required}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      XAI_API_KEY: ${XAI_API_KEY:-}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}
      COURTLISTENER_API_KEY: ${COURTLISTENER_API_KEY:-}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # React frontend (nginx serving built assets)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: fc-portal-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
    driver: local
```

### 7. CREATE `Dockerfile.backend` (in repo root)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8. CREATE `frontend/Dockerfile.frontend`

```dockerfile
FROM node:22-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 9. CREATE `frontend/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — all routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /auth {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /chat {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /specialists {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /usage {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://backend:8000;
    }
}
```

### 10. CREATE `.env.example` (in repo root — update existing)

Replace or update the existing `.env.example` with:

```bash
# Database
DB_USER=portal
DB_PASSWORD=change_me_in_production

# Authentication
JWT_SECRET=change_me_to_random_64_char_string

# LLM Provider API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
XAI_API_KEY=xai-...
GOOGLE_API_KEY=AI...
COURTLISTENER_API_KEY=...

# Optional
DATABASE_URL=postgresql://portal:change_me@localhost:5432/ai_portal
```

---

## Verification Steps

After all files are created:

1. `cd frontend && npm run build` — should complete with 0 errors
2. `cd frontend && npx tsc --noEmit` — should pass type checking
3. `docker compose -f docker-compose.v2.yml config` — should validate without errors
4. Verify no modifications to `backend/` files
5. Verify no modifications to `api/client.ts`, `types/index.ts`, `AuthContext.tsx`

---

## Commit Message

```
feat: Phase 3D — usage dashboard, settings page, Docker Compose production stack

- UsagePage: stats cards, CSS bar chart, usage table with tabs (chat/pipeline)
- SettingsPage: portal info, specialist list, pipeline list, session management
- CostChart: pure CSS horizontal bar chart (no library dependencies)
- UsageTable: sortable table with relative timestamps and cost coloring
- StatsCards: 4 summary metric cards with client-side aggregation
- docker-compose.v2.yml: PostgreSQL + FastAPI backend + React frontend (nginx)
- Dockerfile.backend: Python 3.12 slim, uvicorn
- Dockerfile.frontend: Node 22 build stage, nginx serve stage
- nginx.conf: SPA routing + API proxy + WebSocket upgrade support
- .env.example: updated for v2.0 stack
```
