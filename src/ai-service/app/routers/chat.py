"""Chat endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..core.dependencies import AgentServiceDep
from ..models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(request: ChatRequest, agent_service: AgentServiceDep):
    """
    Stream chat completion responses using Server-Sent Events (SSE).

    Args:
        request: Chat request containing the user message
        agent_service: Injected chat agent service

    Returns:
        StreamingResponse with SSE format
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    async def generate_stream():
        """Generate SSE stream of chat responses."""
        try:
            chunk_count = 0
            async for chunk in agent_service.stream_chat_completion(
                request.message, request.history
            ):
                chunk_count += 1
                logger.debug("Streaming chunk %d: %r", chunk_count, chunk)
                # Format as Server-Sent Events
                yield f"data: {chunk}\n\n"
            # Send completion marker
            logger.info("Stream complete, sent %d chunks", chunk_count)
            yield "data: [DONE]\n\n"
        except Exception as e:
            # Send error in SSE format
            logger.error("Stream error: %s", e, exc_info=True)
            yield f"data: [ERROR: {str(e)}]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, agent_service: AgentServiceDep):
    """
    Get a complete (non-streaming) chat response.

    Args:
        request: Chat request containing the user message
        agent_service: Injected chat agent service

    Returns:
        ChatResponse with the complete response
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        logger.info("Chat request received | stream=%s", request.stream)
        if request.history and request.history.messages:
            logger.debug(
                "History messages received: %s",
                request.history.messages,
            )
        (
            response_text,
            updated_history,
        ) = await agent_service.get_chat_completion(
            request.message,
            request.history,
        )
        logger.info("Chat response length: %d", len(response_text))
        return ChatResponse(response=response_text, history=updated_history)
    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(
            status_code=500, detail=f"Error processing chat request: {str(e)}"
        ) from e
