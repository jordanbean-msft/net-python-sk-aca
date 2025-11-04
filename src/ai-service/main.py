"""Main FastAPI application."""

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.tracing import setup_tracing
from app.routers import chat, health
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Set up OpenTelemetry tracing if enabled
setup_tracing()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Python FastAPI with Semantic Kernel for AI chat completions",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn

    # When running locally with: uv run python main.py
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
