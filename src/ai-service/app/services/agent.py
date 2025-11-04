"""Chat agent service using Semantic Kernel."""

from typing import AsyncGenerator

from azure.identity.aio import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion, AzureChatPromptExecutionSettings)
from semantic_kernel.contents import StreamingChatMessageContent

from ..core.config import settings
from ..models import ChatHistoryModel, chat_history_to_sk, sk_to_chat_history


class ChatAgentService:
    """Service for managing Azure AI Foundry Chat Completion Agent using Semantic Kernel."""

    def __init__(self):
        """Initialize the chat agent service with Azure AI Foundry configuration."""
        self.kernel = Kernel()

        # Configure Azure OpenAI chat completion service
        # Use API key if provided, otherwise use Managed Identity
        if settings.azure_openai_api_key:
            self.chat_service = AzureChatCompletion(
                deployment_name=settings.azure_ai_model_deployment,
                endpoint=settings.azure_ai_project_endpoint,
                api_key=settings.azure_openai_api_key,
            )
        else:
            # Use Managed Identity (best practice for production)
            self.chat_service = AzureChatCompletion(
                deployment_name=settings.azure_ai_model_deployment,
                endpoint=settings.azure_ai_project_endpoint,
                ad_token_provider=DefaultAzureCredential().get_token,
            )

        # Add the service to the kernel
        self.kernel.add_service(self.chat_service)
        # Default execution settings
        self.execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.7,
            top_p=0.95,
            max_tokens=800,
        )

        # System instructions for the agent
        self.system_message = """You are a helpful AI assistant.
You provide clear, accurate, and concise responses to user questions.
You are friendly and professional in your interactions."""

    async def stream_chat_completion(
        self,
        user_message: str,
        chat_history: ChatHistoryModel | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion responses from the Azure AI agent.

        Args:
            user_message: The user's input message
            chat_history: Optional API chat history model for context

        Yields:
            String chunks of the streaming response
        """
        # Initialize chat history if not provided
        if chat_history is None:
            chat_history = ChatHistoryModel()

        # Convert API model to Semantic Kernel ChatHistory
        sk_history = chat_history_to_sk(chat_history, self.system_message)

        # Add user message to history
        sk_history.add_user_message(user_message)

        # Stream the response
        response_text = ""
        async for chunk in self.chat_service.get_streaming_chat_message_contents(
            chat_history=sk_history,
            settings=self.execution_settings,
            kernel=self.kernel,
        ):
            if isinstance(chunk, StreamingChatMessageContent):
                if chunk.content:
                    response_text += chunk.content
                    yield chunk.content

        # Add assistant's response to history
        if response_text:
            sk_history.add_assistant_message(response_text)

    async def get_chat_completion(
        self,
        user_message: str,
        chat_history: ChatHistoryModel | None = None,
    ) -> tuple[str, ChatHistoryModel]:
        """
        Get a non-streaming chat completion response.

        Args:
            user_message: The user's input message
            chat_history: Optional API chat history model for context

        Returns:
            Tuple of (response text, updated chat history)
        """
        # Initialize chat history if not provided
        if chat_history is None:
            chat_history = ChatHistoryModel()

        # Convert API model to Semantic Kernel ChatHistory
        sk_history = chat_history_to_sk(chat_history, self.system_message)

        # Add user message to history
        sk_history.add_user_message(user_message)

        # Get response
        response = await self.chat_service.get_chat_message_contents(
            chat_history=sk_history,
            settings=self.execution_settings,
            kernel=self.kernel,
        )

        # Extract response text
        response_text = ""
        if response and len(response) > 0:
            # Get the content from the chat message
            first_message = response[0]
            if hasattr(first_message, "content") and first_message.content:
                if isinstance(first_message.content, str):
                    response_text = first_message.content
                else:
                    response_text = str(first_message.content)

            # Add to history if we got a response
            if response_text:
                sk_history.add_assistant_message(response_text)

        # Convert back to API model
        updated_history = sk_to_chat_history(sk_history)

        return response_text, updated_history
