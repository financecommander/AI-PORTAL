# Backend v2.0 - Known Limitations and Future Improvements

This document outlines current limitations in the FastAPI backend and planned future enhancements.

## Current Limitations

### 1. Authentication
**Status**: Not Implemented  
**Impact**: Medium  
**Description**: Currently, all requests use a hardcoded `anonymous@example.com` email for usage tracking.

**Current Workaround**: All usage is logged under a single hashed email.

**Future Solution**:
- Implement JWT-based authentication
- Extract user email from validated JWT tokens
- Add authentication dependency to protect endpoints
- Support domain-based access control (existing in Streamlit app)

**Implementation Notes**:
- Can reuse JWT handler from `auth/jwt_handler.py`
- Need to add `Authorization: Bearer <token>` header validation
- Update rate limiter to use user ID from JWT instead of IP

### 2. Streaming Usage Logging
**Status**: Not Implemented  
**Impact**: High  
**Description**: Streaming chat requests (`POST /chat/stream`) do not log usage to the database.

**Current Workaround**: Only non-streaming requests are logged.

**Future Solutions** (in order of preference):
1. **FastAPI BackgroundTasks**: Log usage after SSE stream completes
2. **Message Queue**: Use Redis/RabbitMQ for async processing
3. **Thread Executor**: Use sync session in separate thread

**Implementation Example** (BackgroundTasks):
```python
from fastapi import BackgroundTasks

async def log_streaming_usage(specialist_id, tokens, ...):
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        log = UsageLog(...)
        session.add(log)
        session.commit()

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    # ... streaming logic ...
    if final_chunk:
        background_tasks.add_task(
            log_streaming_usage,
            specialist.id,
            final_chunk.input_tokens,
            # ... other params
        )
```

### 3. Rate Limiting Scope
**Status**: IP-based (Limited)  
**Impact**: Medium  
**Description**: Rate limiting is currently per-IP address, which has several issues:
- Users behind NAT/proxy share the same limit
- Easy to bypass by changing IP
- Doesn't align with per-user billing

**Current Workaround**: Uses `X-Forwarded-For` header when available.

**Future Solution**:
- Switch to per-user rate limiting (requires authentication)
- Support both IP-based (anonymous) and user-based limits
- Configurable limits per user tier/plan

### 4. Rate Limiter Memory Management
**Status**: Partially Addressed  
**Impact**: Low  
**Description**: Token bucket stores unlimited entries in memory.

**Current Solution**: LRU eviction with max 10,000 buckets.

**Future Improvements**:
- Redis-backed rate limiter for distributed systems
- TTL-based cleanup for inactive buckets
- Persistent storage for rate limit state

### 5. Database Migrations
**Status**: Not Implemented  
**Impact**: Low  
**Description**: Schema changes require manual database updates.

**Current Workaround**: SQLModel auto-creates tables on startup.

**Future Solution**:
- Integrate Alembic for database migrations
- Add migration scripts for schema versioning
- Support for zero-downtime deployments

### 6. Error Handling
**Status**: Basic  
**Impact**: Medium  
**Description**: Limited error context and logging.

**Future Improvements**:
- Structured logging with correlation IDs
- Better error messages for clients
- Sentry/monitoring integration
- Retry logic for transient failures

### 7. API Versioning
**Status**: Not Implemented  
**Impact**: Low  
**Description**: No versioning strategy for API endpoints.

**Future Solution**:
- Add `/v1/` prefix to all endpoints
- Support multiple API versions concurrently
- Deprecation warnings in responses

### 8. Performance Optimizations
**Status**: Not Implemented  
**Impact**: Medium  

**Future Improvements**:
- Database connection pooling
- Response caching for common queries
- Async session management improvements
- Prometheus metrics endpoint
- Request/response compression

### 9. Security Enhancements
**Status**: Basic  
**Impact**: High  

**Future Improvements**:
- Input sanitization and validation
- SQL injection prevention (SQLModel provides some protection)
- Rate limit per endpoint (different limits for different operations)
- Request signing for webhook endpoints
- API key support as alternative to JWT

### 10. WebSocket Support
**Status**: Not Implemented  
**Impact**: Low  
**Description**: Only REST endpoints are available. SSE is used for streaming.

**Future Enhancement**:
- Add WebSocket endpoint for bidirectional communication
- Support for multi-turn conversations over persistent connection
- Typing indicators and presence

## Priority Order

### High Priority (P0)
1. Authentication (JWT integration)
2. Streaming usage logging
3. Security enhancements

### Medium Priority (P1)
4. User-based rate limiting
5. Better error handling and logging
6. Performance optimizations

### Low Priority (P2)
7. Database migrations (Alembic)
8. API versioning
9. WebSocket support
10. Rate limiter improvements

## Contributing

When addressing these limitations:
1. Create a new issue referencing this document
2. Update this document when implementing solutions
3. Add tests for new functionality
4. Update README.md with new features

## Testing Strategy

For each limitation addressed:
- [ ] Unit tests for new functionality
- [ ] Integration tests with existing components
- [ ] Load/performance tests where applicable
- [ ] Security audit for authentication/authorization changes
