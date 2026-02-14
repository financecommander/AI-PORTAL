# Technical Debt Log

Items tracked for future improvement. Prioritised by impact.

## High Priority

### 1. Persistent Conversation Storage
**Current:** Conversations are session-only (Streamlit session state). Lost on page refresh.
**Desired:** SQLite or PostgreSQL backend for conversation persistence.
**Effort:** Medium
**Impact:** High — users lose context on refresh.

### 2. Async Throughout
**Current:** Some paths use `asyncio.run()` wrappers around async provider calls.
**Desired:** Full async/await with an async-native web framework or Streamlit's async support.
**Effort:** Medium
**Impact:** Medium — better scalability under concurrent load.

### 3. Structured Logging
**Current:** Usage logging is CSV-based. Application logging uses print/implicit.
**Desired:** Python `logging` module with structured JSON output. Centralized log aggregation.
**Effort:** Low
**Impact:** Medium — better observability in production.

## Medium Priority

### 4. Provider Error Recovery
**Current:** Provider errors bubble up with basic error messages.
**Desired:** Retry with exponential backoff, circuit breaker pattern, fallback to alternate provider.
**Effort:** Medium
**Impact:** Medium — improved reliability.

### 5. Token Counting Accuracy
**Current:** Google and Anthropic providers use `len(text) // 4` heuristic.
**Desired:** Use provider-specific tokenizers (`tiktoken` for OpenAI, etc.).
**Effort:** Low
**Impact:** Low-Medium — more accurate cost estimation.

### 6. Test Coverage for UI Layer
**Current:** `ui/chat_view.py` and `ui/sidebar.py` are tested via integration tests only at the engine level. No Streamlit component testing.
**Desired:** Streamlit `AppTest` or similar for UI component testing.
**Effort:** Medium
**Impact:** Low — UI bugs caught later.

## Low Priority

### 7. Type Checking
**Current:** Type hints present but no CI enforcement.
**Desired:** `mypy` in strict mode, integrated into CI.
**Effort:** Low
**Impact:** Low — catches type errors early.

### 8. Configuration Validation on Startup
**Current:** Missing API keys fail at first use.
**Desired:** Validate all required configuration at app startup with clear error messages.
**Effort:** Low
**Impact:** Low — better developer/admin experience.

### 9. Specialist Versioning UI
**Current:** Prompt history tracked in JSON but not exposed in UI for rollback.
**Desired:** UI for viewing and reverting to previous prompt versions.
**Effort:** Medium
**Impact:** Low — convenience feature for admins.

### 10. Rate Limiter Persistence
**Current:** Rate limits are per-session (in-memory). Reset on restart.
**Desired:** Redis-backed rate limiting for persistence across restarts.
**Effort:** Medium
**Impact:** Low — only matters for sustained abuse scenarios.
