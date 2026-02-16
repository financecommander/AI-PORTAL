# AI Portal Backend v2.0

FastAPI-based backend for multi-agent pipeline execution with real-time WebSocket streaming.

## Features

- **Multi-Agent Pipelines**: CrewAI-powered agent orchestration
- **WebSocket Streaming**: Real-time progress updates during execution
- **Token Tracking**: Comprehensive token usage and cost estimation
- **Pipeline Registry**: Pluggable pipeline architecture
- **Database Logging**: PostgreSQL/SQLite for execution history
- **JWT Authentication**: Secure API access

## Architecture

### Components

- **Pipelines**: Multi-agent execution engines (Lex Intelligence, Calculus, Forge)
- **WebSocket Manager**: Real-time progress broadcasting
- **Token Estimator**: LLM usage tracking and cost calculation
- **Database**: SQLModel ORM with PostgreSQL/SQLite support
- **Authentication**: JWT-based with domain validation

### Pipelines

1. **Lex Intelligence Ultimate**: 6-agent legal research pipeline
   - Legal Research Specialist
   - Statutory Analyst
   - Constitutional Law Expert
   - Contract & Commercial Law Specialist
   - Litigation Strategy Advisor
   - Legal Synthesis & Opinion Drafter

2. **Calculus Intelligence** (Coming Soon): General-purpose reasoning
3. **Forge Intelligence** (Coming Soon): Code generation

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL (optional, SQLite for development)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

3. Initialize database:
```bash
python -m backend.database
```

4. Run the server:
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## API Reference

### Endpoints

#### `GET /api/v2/pipelines/list`
List all available pipelines.

**Authentication**: Required (Bearer token)

**Response**:
```json
{
  "pipelines": [
    {
      "name": "lex_intelligence",
      "display_name": "Lex Intelligence Ultimate",
      "description": "6-agent legal research and opinion drafting pipeline",
      "agents": [...],
      "type": "multi_agent"
    }
  ],
  "count": 3
}
```

#### `POST /api/v2/pipelines/run`
Execute a pipeline.

**Authentication**: Required (Bearer token)

**Request**:
```json
{
  "pipeline_name": "lex_intelligence",
  "query": "What are the legal implications of..."
}
```

**Response**:
```json
{
  "pipeline_id": "uuid",
  "status": "completed",
  "output": "Legal opinion...",
  "total_tokens": 15000,
  "total_cost": 0.45,
  "duration_ms": 45000,
  "agent_breakdown": [...],
  "ws_url": "/api/v2/pipelines/ws/{pipeline_id}"
}
```

#### `WS /api/v2/pipelines/ws/{pipeline_id}`
WebSocket for real-time progress updates.

**Authentication**: Optional (token query parameter)

**Events**:
- `agent_start`: Agent begins execution
- `agent_complete`: Agent finishes execution
- `token_update`: Token usage update
- `error`: Execution error
- `complete`: Pipeline completed

**Event Format**:
```json
{
  "type": "agent_start",
  "pipeline_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "agent": "Legal Research Specialist",
    "input_tokens": 1000
  }
}
```

## Development

### Project Structure

```
backend/
├── auth/                 # JWT authentication
├── config/               # Settings and configuration
├── database/             # Database setup and session management
├── models/               # SQLModel database models
├── pipelines/            # Pipeline implementations
│   ├── base_pipeline.py          # Abstract base class
│   ├── crew_pipeline.py          # CrewAI wrapper
│   ├── lex_intelligence.py       # Legal research pipeline
│   ├── calculus_intelligence.py  # Stub
│   ├── forge_intelligence.py     # Stub
│   └── registry.py               # Pipeline registry
├── routes/               # FastAPI route handlers
├── utils/                # Utilities (token estimator, etc.)
├── websockets/           # WebSocket manager
└── main.py               # FastAPI application
```

### Adding a New Pipeline

1. Create pipeline class inheriting from `BasePipeline`
2. Implement required methods: `execute()`, `get_agents()`, `estimate_cost()`
3. Register in `backend/pipelines/registry.py`

Example:
```python
from backend.pipelines.base_pipeline import BasePipeline, PipelineResult

class MyPipeline(BasePipeline):
    async def execute(self, query, user_hash, on_progress=None):
        # Implementation
        pass
    
    def get_agents(self):
        return [{"name": "Agent", "goal": "Goal", "model": "gpt-4o"}]
    
    def estimate_cost(self, input_length):
        return 0.1

# Register
_REGISTRY["my_pipeline"] = lambda: MyPipeline()
```

### Testing

Run tests:
```bash
python -m pytest backend/tests/ -v
```

## Environment Variables

See `backend/.env.example` for all configuration options.

Required:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `XAI_API_KEY`
- `COURTLISTENER_API_KEY` (for Lex Intelligence)
- `DATABASE_URL` (defaults to SQLite)
- `JWT_SECRET_KEY` (change in production)

## Deployment

### Docker

```bash
docker build -t ai-portal-backend .
docker run -p 8000:8000 --env-file backend/.env ai-portal-backend
```

### Production

1. Use PostgreSQL for production database
2. Set strong `JWT_SECRET_KEY`
3. Configure CORS origins in `backend/main.py`
4. Enable HTTPS
5. Set `DEBUG=false`

## License

[Add license information]
