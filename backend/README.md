# AI Portal Backend v2.0

FastAPI backend providing REST API endpoints for the FinanceCommander AI Portal.

## Features

- **Non-streaming Chat Endpoint** (`POST /chat/send`): Synchronous chat interactions
- **Streaming Chat Endpoint** (`POST /chat/stream`): Server-Sent Events (SSE) for real-time streaming
- **Token Bucket Rate Limiter**: 60 requests/hour per client IP
- **PostgreSQL Usage Logging**: Comprehensive interaction tracking
- **Specialist Validation**: Integration with existing specialist manager
- **Multi-Provider Support**: OpenAI, Anthropic, Google via factory pattern

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in the project root:

```env
# Provider API Keys
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-key

# Database (SQLite for dev, PostgreSQL for production)
DATABASE_URL=sqlite:///./ai_portal.db
# DATABASE_URL=postgresql://user:password@localhost/ai_portal

# Rate Limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=3600

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8501"]
```

### Run the Backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once running, visit:
- **Interactive docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

### POST /chat/send

Non-streaming chat endpoint.

**Request:**
```json
{
  "specialist_id": "specialist-uuid",
  "message": "What is the capital of France?",
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{
  "content": "The capital of France is Paris.",
  "specialist_id": "specialist-uuid",
  "specialist_name": "General Assistant",
  "provider": "openai",
  "model": "gpt-4o",
  "input_tokens": 45,
  "output_tokens": 12,
  "estimated_cost_usd": 0.000123,
  "latency_ms": 1234.5
}
```

### POST /chat/stream

Streaming chat endpoint using Server-Sent Events.

**Request:** Same as `/chat/send`

**Response:** SSE stream of chunks:
```
event: message
data: {"content": "The", "is_final": false, "input_tokens": 0, "output_tokens": 0, "model": "", "latency_ms": 0.0}

event: message
data: {"content": " capital", "is_final": false, "input_tokens": 0, "output_tokens": 0, "model": "", "latency_ms": 0.0}

event: message
data: {"content": "", "is_final": true, "input_tokens": 45, "output_tokens": 12, "model": "gpt-4o", "latency_ms": 1234.5}
```

### Rate Limiting

All requests include rate limit headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Seconds until bucket refills

When rate limit is exceeded, returns `429 Too Many Requests` with `Retry-After` header.

## Database Schema

### UsageLog Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| timestamp | DateTime | Request timestamp (UTC) |
| user_email_hash | String | SHA-256 hash of user email |
| specialist_id | String | Specialist UUID |
| specialist_name | String | Specialist display name |
| provider | String | LLM provider (openai, anthropic, google) |
| model | String | Model identifier |
| input_tokens | Integer | Input token count |
| output_tokens | Integer | Output token count |
| estimated_cost_usd | Float | Estimated cost in USD |
| latency_ms | Float | Request latency in milliseconds |
| success | Boolean | Whether request succeeded |

## Architecture

```
backend/
├── main.py              # FastAPI application
├── config/
│   └── settings.py      # Configuration via Pydantic
├── database/
│   └── session.py       # SQLModel engine and session management
├── middleware/
│   └── rate_limiter.py  # Token bucket rate limiter
├── models/
│   ├── chat.py          # Request/response models
│   └── usage_log.py     # Database models
└── routes/
    └── chat.py          # Chat endpoints
```

## Testing

Run backend tests:

```bash
python -m pytest backend/tests/ -v
```

## Integration with Existing Codebase

The backend integrates with existing components:
- **Specialist Manager**: Uses `specialists/manager.py` for validation
- **Provider Factory**: Uses `providers/` for LLM interactions
- **Pricing**: Uses `config/pricing.py` for cost estimation
- **Base Provider**: Compatible with `providers/base.py` interfaces

## Future Enhancements

- [ ] JWT authentication integration
- [ ] User-based rate limiting (vs IP-based)
- [ ] WebSocket support for real-time chat
- [ ] Background task queue for async logging in streaming mode
- [ ] Prometheus metrics endpoint
- [ ] Database migrations with Alembic
