# Administrator Guide

## Overview

This guide covers day-to-day administration of the FinanceCommander AI Portal including specialist management, monitoring usage, and troubleshooting.

## Managing Specialists

### Creating a Specialist

Specialists are AI personas with fixed system prompts, models, and parameters.

**Via the UI:**
1. Open the sidebar → **Manage Specialists** → **Create** tab
2. Fill in name, description, provider, model, system prompt
3. Set temperature (0.0–1.0) and max tokens (100–128,000)
4. Click **Create**

**Via JSON:**
Edit `config/specialists.json` directly. Each specialist requires:

```json
{
  "id": "unique_id",
  "name": "Display Name",
  "description": "What this specialist does",
  "provider": "openai|anthropic|google",
  "model": "gpt-4o",
  "system_prompt": "You are...",
  "temperature": 0.5,
  "max_tokens": 4096,
  "pricing": {
    "input_per_1m": 2.50,
    "output_per_1m": 10.00
  }
}
```

### Duplicating a Specialist

Use the **Duplicate** tab in **Manage Specialists** to clone an existing specialist with a new ID and " (Copy)" suffix. Useful for A/B testing different prompts.

### Pinning Specialists

Click the 📌 button next to a specialist in the selector. Pinned specialists appear first in the dropdown.

## Monitoring Usage

### Usage Logs

Daily CSV files are written to `logs/usage_YYYY-MM-DD.csv` with columns:

| Column | Description |
|--------|-------------|
| `timestamp` | ISO 8601 UTC timestamp |
| `user_email_hash` | SHA-256 hash of user email |
| `specialist_id` | Specialist identifier |
| `specialist_name` | Display name |
| `provider` | openai / anthropic / google |
| `model` | Model name |
| `input_tokens` | Input token count |
| `output_tokens` | Output token count |
| `estimated_cost_usd` | Estimated cost |
| `latency_ms` | Response latency |
| `success` | True/False |

### Cost Reports

Generate reports using the cost report script:

```bash
# Full report (Markdown)
python scripts/cost_report.py

# Last 7 days, CSV format
python scripts/cost_report.py --days 7 --format csv

# Custom log directory
python scripts/cost_report.py --log-dir /path/to/logs
```

### In-App Stats

The sidebar shows per-specialist usage stats (request count, total cost) for the selected specialist.

## Configuration

### Key Settings (`config/settings.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_MODEL` | `gpt-4o` | Fallback model when no specialist selected |
| `DEFAULT_TEMPERATURE` | `0.7` | Default temperature |
| `STREAMING_ENABLED` | `True` | Enable/disable streaming responses |
| `SESSION_TIMEOUT_SECONDS` | `3600` | Session timeout (1 hour) |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per session |
| `MAX_CONVERSATION_LENGTH` | `50` | Max messages before auto-truncation |
| `LOG_DIR` | `logs` | Usage log directory |

### Pricing (`config/pricing.py`)

Token pricing is defined in `MODEL_PRICING` dict. Update prices when providers change their rates:

```python
MODEL_PRICING = {
    "gpt-4o": (2.50, 10.00),  # (input_per_1m, output_per_1m)
    ...
}
```

### Theme (`.streamlit/config.toml`)

Customize the portal appearance:

```toml
[theme]
primaryColor = "#2E75B6"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F7FA"
textColor = "#1A1A1A"
```

## Troubleshooting

### "Provider API key required"

Ensure the relevant environment variable is set:
```bash
echo $OPENAI_API_KEY      # Should not be empty
echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY
```

### Rate Limit Errors

If users hit rate limits, increase `RATE_LIMIT_REQUESTS` in `config/settings.py` or restart the session.

### High Latency

Check the usage logs for `latency_ms` values. If consistently high:
- Switch to a faster model (e.g., `gpt-4o-mini` instead of `gpt-4o`)
- Enable streaming for perceived performance improvement
- Check network connectivity to provider APIs

### File Upload Failures

- Verify file extension is in the allowed list (`.txt`, `.csv`, `.json`, `.py`, `.md`, `.pdf`, `.png`, `.jpg`, `.jpeg`)
- Check file size is under 10MB
- For PDF issues, ensure `pdfplumber` is installed

## Backup & Recovery

### Specialist Configurations

Back up `config/specialists.json` regularly:
```bash
cp config/specialists.json config/specialists.json.bak
```

### Usage Logs

Usage logs are append-only CSV files. Back up the `logs/` directory:
```bash
tar czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```
