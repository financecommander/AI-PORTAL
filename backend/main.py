"""FastAPI backend application for AI Portal v2.0."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.database import init_db
from backend.routes import pipelines
from backend.routes import auth as auth_routes
from backend.routes import chat as chat_routes
from backend.routes import specialists as specialist_routes
from backend.routes import usage as usage_routes
from backend.errors.exceptions import PortalError
from backend.middleware.rate_limiter import RateLimiterMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FinanceCommander AI Portal",
    description="Multi-agent intelligence platform",
    version="2.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
@app.exception_handler(PortalError)
async def portal_error_handler(request: Request, exc: PortalError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

# Routes
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
app.include_router(specialist_routes.router, prefix="/specialists", tags=["specialists"])
app.include_router(usage_routes.router, prefix="/usage", tags=["usage"])
app.include_router(pipelines.router, prefix="/api/v2", tags=["pipelines"])


@app.get("/")
async def root():
    return {"message": "FinanceCommander AI Portal v2.0", "docs": "/docs", "status": "operational"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}
