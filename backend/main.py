"""
FastAPI application for FinanceCommander AI Portal v2.0.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.errors import PortalError
from backend.database import init_db
from backend.middleware.rate_limiter import RateLimitMiddleware
from backend.routes import auth, chat, specialists, pipelines, usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for FinanceCommander AI Portal",
    version="2.0.0",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Global exception handler for PortalError
@app.exception_handler(PortalError)
async def portal_error_handler(request: Request, exc: PortalError):
    """Handle PortalError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "2.0.0",
    }


# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(specialists.router)
app.include_router(pipelines.router)
app.include_router(usage.router)
