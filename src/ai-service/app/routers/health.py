"""Health check endpoints."""

from fastapi import APIRouter

from ..core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat_stream": "/chat/stream (POST)",
            "chat": "/chat (POST)",
        },
    }
