# Deployment Guide

## Prerequisites

- Python 3.10 or higher
- At least one LLM provider API key (OpenAI, Anthropic, or Google)
- Git

## Option 1: Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/financecommander/AI-PORTAL.git
cd AI-PORTAL
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file or export directly:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIzaSy..."

# Optional
export PORTAL_ADMIN_EMAIL="admin@yourcompany.com"
export STREAMLIT_SERVER_PORT=8501
```

### 5. Run the Application

```bash
streamlit run app.py
```

The portal will be available at `http://localhost:8501`.

---

## Option 2: Docker

### 1. Build the Image

```bash
docker build -t ai-portal .
```

### 2. Run the Container

```bash
docker run -d \
  --name ai-portal \
  -p 8501:8501 \
  -e OPENAI_API_KEY="sk-..." \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e GOOGLE_API_KEY="AIzaSy..." \
  -v ai-portal-logs:/app/logs \
  ai-portal
```

### 3. Using Docker Compose

```bash
docker compose up -d
```

See `docker-compose.yml` for the full configuration.

---

## Option 3: Streamlit Community Cloud

### 1. Fork or Push to GitHub

Ensure your repository is on GitHub.

### 2. Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your repository, branch (`main`), and file (`app.py`)
4. Under **Advanced settings**, add your API keys as secrets:

```toml
# .streamlit/secrets.toml (do NOT commit this file)
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_API_KEY = "AIzaSy..."
```

### 3. Deploy

Click **Deploy** and your app will be live at `https://your-app.streamlit.app`.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | At least one provider key | OpenAI API key |
| `ANTHROPIC_API_KEY` | At least one provider key | Anthropic API key |
| `GOOGLE_API_KEY` | At least one provider key | Google AI API key |
| `OPENAI_API_BASE` | No | Custom OpenAI-compatible base URL (for Grok, etc.) |
| `PORTAL_ADMIN_EMAIL` | No | Admin email for elevated access |
| `STREAMLIT_SERVER_PORT` | No | Server port (default: 8501) |

## Health Check

The application serves on port 8501 by default. Verify with:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
# Expected: 200
```

## Logs

Usage logs are written to `logs/usage_YYYY-MM-DD.csv`. In Docker, mount the `/app/logs` volume for persistence.

Generate a cost report:

```bash
python scripts/cost_report.py                 # Markdown output
python scripts/cost_report.py --format csv     # CSV output
python scripts/cost_report.py --days 7         # Last 7 days only
```

## Running Tests

```bash
# All tests (excluding live API tests)
python -m pytest tests/ -m "not live" -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# Performance benchmarks
python -m pytest tests/performance/ -v

# Live API tests (requires API keys)
python -m pytest tests/live/ -v -m live
```
