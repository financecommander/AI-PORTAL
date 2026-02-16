# FinanceCommander AI Portal v2.0 Backend

FastAPI-based backend for FinanceCommander AI Portal v2.0 with database persistence, authentication, and LLM provider integration.

## Features

### Phase 1A
- **Database Models**: SQLModel-based models for usage tracking and pipeline runs
- **Authentication**: JWT-based authentication with domain validation
- **FastAPI Application**: CORS middleware, global exception handling, and health checks
- **Database Logging**: Usage and pipeline run tracking with SHA-256 email hashing
- **Comprehensive Tests**: 42 unit and integration tests

### Phase 1B (Current)
- **Chat Endpoints**: Non-streaming and SSE-based streaming chat
- **Rate Limiting**: Token bucket rate limiter (60 req/hour per IP)
- **Specialist CRUD**: Error-raising CRUD methods for specialist management
- **Usage Tracking**: Comprehensive PostgreSQL logging with cost estimation
- **Multi-Provider Support**: OpenAI, Anthropic, Google via factory pattern

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL (production) or SQLite (development)

### Installation

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example ../.env
# Edit .env with your configuration
```

4. For development, use SQLite in `.env`:
```
DATABASE_URL=sqlite:///./test.db
```

5. For production, use PostgreSQL in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ai_portal
```

## Running the Application

### Development Server

From the repository root:
```bash
cd /path/to/AI-PORTAL
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --ws none
```

### Testing

Run all tests:
```bash
cd backend
python -m pytest tests/ -v
```

Run specific test categories:
```bash
# Unit tests only
python -m pytest tests/test_authenticator.py tests/test_jwt_handler.py -v

# Integration tests
python -m pytest tests/test_integration.py -v
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Authentication
```bash
POST /auth/login
Content-Type: application/json
{
  "email": "user@financecommander.com"
}
```

### Chat
```bash
# Non-streaming
POST /chat/send
Content-Type: application/json
{
  "specialist_id": "uuid",
  "message": "Your query",
  "conversation_history": []
}

# Streaming (SSE)
POST /chat/stream
Content-Type: application/json
{
  "specialist_id": "uuid",
  "message": "Your query",
  "conversation_history": []
}
```

### Swagger UI
Access interactive API documentation at:
```
http://localhost:8000/docs
```

## Project Structure

```
backend/
├── auth/                   # Authentication modules
│   ├── authenticator.py    # Domain validation
│   └── jwt_handler.py      # JWT token creation/verification
├── config/                 # Configuration
│   └── settings.py         # Pydantic settings
├── database/               # Database operations
│   └── __init__.py         # init_db, log_usage, log_pipeline_run
├── errors/                 # Custom exceptions
│   └── __init__.py         # PortalError hierarchy
├── models/                 # Database models
│   └── __init__.py         # UsageLog, PipelineRun
├── middleware/             # Middleware
│   └── rate_limiter.py     # Token bucket rate limiting
├── routes/                 # API routes
│   ├── auth.py             # Authentication routes
│   ├── chat.py             # Chat endpoints (streaming & non-streaming)
│   ├── specialists.py      # Specialist routes (stub)
│   ├── pipelines.py        # Pipeline routes (stub)
│   └── usage.py            # Usage routes (stub)
├── tests/                  # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_authenticator.py
│   ├── test_factory.py
│   ├── test_integration.py
│   ├── test_jwt_handler.py
│   ├── test_providers.py
│   └── test_token_estimator.py
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
└── pytest.ini              # Pytest configuration
```

## Database Models

### UsageLog
Tracks per-request usage metrics:
- `user_email_hash`: SHA-256 hashed email
- `specialist_id`, `specialist_name`: Optional specialist info
- `provider`, `model`: LLM provider and model used
- `input_tokens`, `output_tokens`: Token counts
- `estimated_cost_usd`: Estimated cost
- `latency_ms`: Request latency
- `success`: Request success status

### PipelineRun
Tracks high-level pipeline execution:
- `user_email_hash`: SHA-256 hashed email
- `pipeline_name`: Name of the pipeline
- `status`: running, completed, or failed
- `total_tokens`, `total_cost_usd`: Aggregate metrics
- `duration_ms`: Total execution time
- `error_message`: Optional error details
- `metadata_json`: Additional metadata as JSON string

## Security

- Email addresses are SHA-256 hashed before storage
- JWT tokens for authentication
- Domain-based access control
- CORS middleware for cross-origin requests
- No plaintext secrets in code

## Testing

The test suite includes:
- **9 tests** for authenticator (domain validation, email processing)
- **5 tests** for JWT handler (token creation, verification, expiration)
- **6 tests** for provider factory and instantiation
- **8 tests** for token estimation and pricing
- **14 tests** for integration (API endpoints)

All 42 tests pass with no failures.

## Development Roadmap

### Phase 1B (Next)
- Specialist CRUD operations
- Chat route implementation
- Rate limiting middleware
- WebSocket support for streaming

### Phase 1C (Future)
- Pipeline orchestration
- Usage analytics
- Advanced error recovery
- Monitoring and observability

## License

[Add license information]

## Contributing

[Add contribution guidelines]
