"""Application lifespan management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .dependencies import get_agent_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize the agent service
    get_agent_service()
    yield
    # Shutdown: cleanup if needed
