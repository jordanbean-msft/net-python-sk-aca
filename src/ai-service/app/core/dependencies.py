"""FastAPI dependency injection functions."""

from typing import Annotated

from fastapi import Depends

from ..services.agent import ChatAgentService

# Singleton instance
_agent_service: ChatAgentService | None = None


def get_agent_service() -> ChatAgentService:
    """
    Get or create the singleton agent service instance.

    This is a FastAPI dependency that provides the ChatAgentService.
    The service is initialized once and reused across requests.

    Returns:
        ChatAgentService: The singleton chat agent service instance
    """
    global _agent_service
    if _agent_service is None:
        _agent_service = ChatAgentService()
    return _agent_service


# Type alias for injecting the agent service
AgentServiceDep = Annotated[ChatAgentService, Depends(get_agent_service)]
