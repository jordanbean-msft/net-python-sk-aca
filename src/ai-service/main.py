"""Main FastAPI application."""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.telemetry import setup_telemetry
from app.routers import chat, health

# Configure Python logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress verbose loggers from Azure SDK, httpx, and Semantic Kernel
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.agents").setLevel(logging.WARNING)
logging.getLogger("semantic_kernel.agents.runtime").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Set up Application Insights telemetry
setup_telemetry()

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


# Middleware to suppress health check logs
@app.middleware("http")
async def suppress_health_logs(request: Request, call_next):
    """Suppress logging for health check endpoints."""
    response = await call_next(request)
    # Don't log health checks
    if request.url.path in ["/health", "/"]:
        return response
    # Log other requests at trace level
    logging.getLogger("uvicorn.access").log(
        logging.DEBUG, f"{request.method} {request.url.path}"
    )
    return response


# Include routers
app.include_router(health.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn

    # When running locally with: uv run python main.py
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", settings.log_level).lower()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=log_level,
    )
