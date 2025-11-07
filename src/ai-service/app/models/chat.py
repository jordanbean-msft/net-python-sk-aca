"""Custom chat models for API communication."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of the message sender."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Individual chat message."""

    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")


class ChatHistoryModel(BaseModel):
    """Chat history for API communication between C# and Python."""

    messages: list[ChatMessage] = Field(
        default_factory=list, description="List of chat messages in chronological order"
    )

    def add_message(self, role: MessageRole, content: str) -> None:
        """Add a message to the chat history."""
        self.messages.append(ChatMessage(role=role, content=content))

    def add_system_message(self, content: str) -> None:
        """Add a system message to the chat history."""
        self.add_message(MessageRole.SYSTEM, content)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the chat history."""
        self.add_message(MessageRole.USER, content)

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the chat history."""
        self.add_message(MessageRole.ASSISTANT, content)


class ChatRequest(BaseModel):
    """Chat request model for API endpoints."""

    message: str = Field(..., description="User message to send")
    history: Optional[ChatHistoryModel] = Field(
        default=None, description="Optional chat history for context"
    )
    stream: bool = Field(default=True, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Chat response model for non-streaming responses."""

    response: str = Field(..., description="Assistant's response message")
    history: ChatHistoryModel = Field(..., description="Updated chat history")
