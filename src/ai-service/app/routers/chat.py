"""Chat endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..core.dependencies import AgentServiceDep
from ..models import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(
    request: ChatRequest, agent_service: AgentServiceDep
):
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
            async for chunk in agent_service.stream_chat_completion(
                request.message, request.history
            ):
                # Format as Server-Sent Events
                yield f"data: {chunk}\n\n"
            # Send completion marker
            yield "data: [DONE]\n\n"
        except Exception as e:
            # Send error in SSE format
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
        response_text, updated_history = await agent_service.get_chat_completion(
            request.message, request.history
        )
        return ChatResponse(response=response_text, history=updated_history)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing chat request: {str(e)}"
        ) from e
