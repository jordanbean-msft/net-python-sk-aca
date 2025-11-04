"""Converter utilities for chat models."""

from semantic_kernel.contents import ChatHistory

from .chat import ChatHistoryModel, MessageRole


def chat_history_to_sk(
    history: ChatHistoryModel, system_message: str | None = None
) -> ChatHistory:
    """
    Convert API ChatHistoryModel to Semantic Kernel ChatHistory.

    Args:
        history: The API chat history model
        system_message: Optional system message to add if no system message exists

    Returns:
        Semantic Kernel ChatHistory object
    """
    sk_history = ChatHistory()

    # Check if there's already a system message
    has_system_message = any(msg.role == MessageRole.SYSTEM for msg in history.messages)

    # Add system message if needed
    if not has_system_message and system_message:
        sk_history.add_system_message(system_message)

    # Convert all messages
    for message in history.messages:
        if message.role == MessageRole.SYSTEM:
            sk_history.add_system_message(message.content)
        elif message.role == MessageRole.USER:
            sk_history.add_user_message(message.content)
        elif message.role == MessageRole.ASSISTANT:
            sk_history.add_assistant_message(message.content)

    return sk_history


def sk_to_chat_history(sk_history: ChatHistory) -> ChatHistoryModel:
    """
    Convert Semantic Kernel ChatHistory to API ChatHistoryModel.

    Args:
        sk_history: The Semantic Kernel ChatHistory object

    Returns:
        API ChatHistoryModel
    """
    history = ChatHistoryModel()

    for message in sk_history.messages:
        role_str = str(message.role).lower()
        if role_str == "system":
            history.add_system_message(message.content)
        elif role_str == "user":
            history.add_user_message(message.content)
        elif role_str == "assistant":
            history.add_assistant_message(message.content)

    return history
