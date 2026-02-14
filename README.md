# FinanceCommander AI Portal

A secure, multi-provider AI chat portal designed for financial analysis and decision-making. Built with Streamlit and supporting OpenAI, Anthropic Claude, and Google Gemini models.

## Features

- **Multi-Provider Support**: Choose from OpenAI GPT, Anthropic Claude, or Google Gemini models
- **Specialist Roles**: Pre-configured AI specialists for different financial domains
- **Secure Authentication**: Domain-based email authentication with SHA-256 hashing
- **Usage Logging**: Comprehensive CSV logging with cost estimation and performance metrics
- **Real-time Chat**: Interactive chat interface with conversation history

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

Run the test suite:
```bash
pytest tests/
```

### Project Structure

```
├── app.py                 # Main Streamlit application
├── auth/                  # Authentication module
├── chat/                  # Chat engine and logging
├── config/                # Configuration and settings
├── providers/             # LLM provider implementations
├── specialists/           # AI specialist management
├── ui/                    # Streamlit UI components
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
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
