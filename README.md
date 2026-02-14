# FinanceCommander AI Portal

A secure, multi-provider AI chat portal designed for financial analysis and decision-making. Built with Streamlit and supporting OpenAI, Anthropic Claude, Google Gemini, and Grok models.

## Features

### Core (v0.1)
- **Multi-Provider Support**: Choose from OpenAI GPT, Anthropic Claude, Google Gemini, or Grok models
- **Specialist Roles**: Pre-configured AI specialists for different financial domains
- **Secure Authentication**: Domain-based email authentication with SHA-256 hashing
- **Usage Logging**: Comprehensive CSV logging with cost estimation and performance metrics
- **Real-time Chat**: Interactive chat interface with conversation history

### Week 2 (v0.2)
- **Streaming Responses**: Real-time token-by-token streaming for all providers with markdown cursor
- **Specialist CRUD Management**: Add, edit, and delete specialists from the sidebar UI
- **Input Validation**: Comprehensive validation for specialist fields (name, provider, model, temperature, max_tokens, etc.)
- **Session Timeout**: 30-minute inactivity timeout with automatic logout
- **Rate Limiting**: Token-bucket rate limiter (60 requests/hour) with remaining count display
- **Conversation Export**: Download chat history as JSON per specialist
- **Expanded Model Support**: o1, o3-mini, Claude Opus/Sonnet/Haiku 4, Gemini 2.0, Grok 3

### Week 3 (v0.3)
- **File Upload Support**: Attach text, CSV, JSON, Python, Markdown, PDF, and image files to messages
- **Conversation Search**: Case-insensitive search across chat history with recency ranking
- **Specialist Duplication**: Clone specialist configurations for A/B testing
- **Specialist Pinning**: Pin frequently-used specialists to the top of the selector
- **Usage Stats**: Per-specialist request count, token usage, cost, and latency metrics
- **UI Polish**: Custom theme, relative timestamps, token info per message, regenerate button, status panel

### Week 4 (v0.4)
- **Test Restructure**: Organised into unit, integration, live, and performance categories
- **Integration Tests**: End-to-end tests for chat flows, streaming, file upload, and specialist CRUD
- **Performance Benchmarks**: Timed assertions for search, file processing, and conversation operations
- **Cost Report Script**: Markdown/CSV reports grouped by date, provider, model, and specialist

### Week 5 (v1.0.0)
- **Architecture Documentation**: Mermaid diagrams for system, data flow, and test architecture
- **Deployment Guide**: Local, Docker, and Streamlit Cloud deployment instructions
- **Docker Support**: `Dockerfile` + `docker-compose.yml` with health checks
- **Security Hardening**: pip-audit scan, security checklist, input sanitisation audit
- **Admin Guide**: Specialist management, monitoring, configuration, and troubleshooting
- **Tech Debt Log**: Prioritised backlog of known improvements

## Architecture

### Core Components

- **Authentication**: Domain-based user validation
- **Specialists**: Configurable AI roles with custom prompts and model settings
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
