"""FastAPI backend v2.0 main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.pipelines import router as pipelines_router

app = FastAPI(
    title="AI Portal Backend v2.0",
    description="FastAPI-based backend for AI Portal with pipeline orchestration",
    version="2.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipelines_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Portal Backend v2.0",
        "version": "2.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
