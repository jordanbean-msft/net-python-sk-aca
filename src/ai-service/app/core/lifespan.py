"""Application lifespan management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .dependencies import get_agent_service
from .telemetry import setup_telemetry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize telemetry and agent service
    setup_telemetry()
    get_agent_service()
    yield
    # Shutdown: cleanup if needed
