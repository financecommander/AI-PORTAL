"""
FastAPI application for FinanceCommander AI Portal v2.0.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.errors import PortalError
from backend.logging import init_db
from backend.routes import auth, chat, specialists, pipelines, usage


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for FinanceCommander AI Portal",
    version="2.0.0",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
