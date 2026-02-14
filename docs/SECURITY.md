# Security Checklist

## Dependency Security

- [x] `pip-audit` scan: **No known vulnerabilities** (last run: v1.0.0 release)
- [x] All dependencies pinned with minimum versions in `requirements.txt`
- [x] `.dockerignore` excludes `.env`, secrets, and build artifacts
- [x] `.streamlit/secrets.toml` excluded from version control

## Authentication & Session Management

- [x] User emails hashed (SHA-256) before logging — no PII in CSV files
- [x] Session timeout enforced (`SESSION_TIMEOUT_SECONDS` in settings)
- [x] Rate limiting per user session (`RATE_LIMIT_REQUESTS` in settings)
- [x] Admin email configurable via environment variable

## Input Validation

- [x] File upload: extension whitelist (`ALLOWED_EXTENSIONS` in `file_handler.py`)
- [x] File upload: size limit enforced (`MAX_FILE_SIZE_MB = 10`)
- [x] File content: UTF-8 decode with `errors="replace"` — no crash on malformed input
- [x] Specialist names: length limits enforced in validation
- [x] System prompts: length limits enforced in validation
- [x] Temperature/max_tokens: range validation
- [x] Base URL: HTTPS-only enforcement for custom API endpoints
- [x] `ValidationError` raised for all input failures (typed exception)

## API Key Security

- [x] API keys loaded from environment variables only — never hardcoded
- [x] Keys not logged or exposed in usage CSV files
- [x] Provider errors sanitized before display (no key leakage)

## Data Protection

- [x] Usage logs store hashed emails, not raw addresses
- [x] Conversation history stored in session state only (not persisted to disk)
- [x] PDF text extraction runs locally (pdfplumber) — no data sent to third parties for parsing
- [x] File content base64-encoded in memory, not written to disk

## Docker Security

- [x] Slim base image (`python:3.12-slim`)
- [x] Non-essential packages not installed
- [x] Health check endpoint configured
- [x] No root-level secrets in image layers

## Recommendations for Production

- [ ] Add HTTPS termination (reverse proxy with TLS)
- [ ] Implement RBAC for multi-user environments
- [ ] Add audit logging for admin actions
- [ ] Configure CSP headers via reverse proxy
- [ ] Rotate API keys on a schedule
- [ ] Set up automated `pip-audit` in CI/CD pipeline
- [ ] Consider encrypting usage logs at rest
