"""Chat agent service using Semantic Kernel."""

import logging
from typing import AsyncGenerator

from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents import (
    FunctionCallContent,
    StreamingChatMessageContent,
    TextContent,
)
from semantic_kernel.contents.chat_message_content import FinishReason

from ..core.config import settings
from ..models import ChatHistoryModel, chat_history_to_sk, sk_to_chat_history
from ..plugins import WeatherPlugin

logger = logging.getLogger(__name__)


class ChatAgentService:
    """Manage Azure AI chat completions via Semantic Kernel."""

    def __init__(self):
        """Initialize the chat agent service."""
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
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            self.chat_service = AzureChatCompletion(
                deployment_name=settings.azure_ai_model_deployment,
                endpoint=settings.azure_ai_project_endpoint,
                ad_token_provider=token_provider,
            )

        # Add the service to the kernel
        self.kernel.add_service(self.chat_service)

        # Register weather plugin
        self.kernel.add_plugin(WeatherPlugin(), plugin_name="weather")

        # Default execution settings with function calling enabled
        self.execution_settings = AzureChatPromptExecutionSettings(
            temperature=0.7,
            top_p=0.95,
            max_tokens=800,
            function_choice_behavior=FunctionChoiceBehavior.Auto(),
        )

        # System instructions for the agent
        self.system_message = (
            "You are a helpful AI assistant.\n"
            "You provide clear, accurate, and concise responses to user"
            " questions.\n"
            "You are friendly and professional in your interactions.\n"
            "You have access to a weather tool that can provide current"
            " weather information for any location."
        )

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
        logger.info("Starting streaming for message: %s", user_message)
        chunk_count = 0
        last_finish_reason: FinishReason | None = None
        get_stream = self.chat_service.get_streaming_chat_message_contents
        async for chunk in get_stream(
            chat_history=sk_history,
            settings=self.execution_settings,
            kernel=self.kernel,
        ):
            chunk_count += 1
            # Semantic Kernel returns a list, get the first item
            if isinstance(chunk, list) and len(chunk) > 0:
                chunk = chunk[0]

            if isinstance(chunk, StreamingChatMessageContent):
                last_finish_reason = getattr(
                    chunk,
                    "finish_reason",
                    last_finish_reason,
                )
                # Check for function/tool calls in the chunk
                has_text_items = False
                if hasattr(chunk, "items") and chunk.items:
                    for item in chunk.items:
                        if isinstance(item, FunctionCallContent):
                            # Only log complete function calls
                            if item.name:
                                logger.info(
                                    "LLM requested tool call: "
                                    "function='%s', plugin='%s', arguments=%s",
                                    item.name,
                                    getattr(item, "plugin_name", "N/A"),
                                    item.arguments,
                                )
                        if isinstance(item, TextContent) and item.text:
                            logger.debug("Streaming text item: %r", item.text)
                            response_text += item.text
                            yield item.text
                            has_text_items = True

                # Only yield chunk.content if no items were yielded
                if chunk.content and not has_text_items:
                    response_text += chunk.content
                    yield chunk.content

        logger.debug("Streaming complete. Total text: %d chars", len(response_text))
        if last_finish_reason == FinishReason.CONTENT_FILTER and not response_text:
            logger.warning("Streaming completion blocked by content filter")
            response_text = (
                "I'm sorry, but I can't help with that request. "
                "It may involve content that cannot be shared."
            )
            yield response_text
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
            logger.info(
                "Received %d message(s) from chat service",
                len(response),
            )
            logger.debug("First message payload repr: %r", first_message)
            logger.debug(
                "First message fields: role=%s has_items=%s has_content=%s",
                getattr(first_message, "role", None),
                bool(getattr(first_message, "items", None)),
                bool(getattr(first_message, "content", None)),
            )

            # Check for function/tool calls in the response
            text_parts: list[str] = []
            finish_reason = getattr(first_message, "finish_reason", None)
            if finish_reason == FinishReason.CONTENT_FILTER:
                filter_details = None
                inner = getattr(first_message, "inner_content", None)
                if inner and getattr(inner, "choices", None):
                    filter_details = getattr(
                        inner.choices[0],
                        "content_filter_results",
                        None,
                    )
                logger.warning(
                    "Chat completion blocked by content filter: %s",
                    filter_details,
                )
                response_text = (
                    "I'm sorry, but I can't help with that request. "
                    "It may involve content that cannot be shared."
                )

            if hasattr(first_message, "items") and first_message.items:
                for item in first_message.items:
                    logger.debug(
                        "Response content item type=%s payload=%r",
                        type(item),
                        item,
                    )
                    if isinstance(item, FunctionCallContent):
                        logger.info(
                            "LLM requested tool call: "
                            "function='%s', plugin='%s', arguments=%s",
                            item.name,
                            getattr(item, "plugin_name", "N/A"),
                            item.arguments,
                        )
                    if isinstance(item, TextContent) and item.text:
                        text_parts.append(item.text)

            if hasattr(first_message, "content") and first_message.content:
                if isinstance(first_message.content, str):
                    response_text = first_message.content
                else:
                    logger.debug(
                        "Non-string content type: %s",
                        type(first_message.content),
                    )
                    # Some SDKs return content blocks such as TextContent
                    if isinstance(first_message.content, list):
                        for item in first_message.content:
                            logger.debug(
                                "Content item type=%s value=%r",
                                type(item),
                                item,
                            )
                            item_text = getattr(item, "text", None)
                            if item_text:
                                text_parts.append(item_text)

                # Fallback to string conversion if we still have no text
                if not response_text and not text_parts:
                    response_text = str(first_message.content)

            if not response_text and text_parts:
                response_text = "".join(text_parts)

            # Add to history if we got a response
            if response_text:
                sk_history.add_assistant_message(response_text)

        # Convert back to API model
        updated_history = sk_to_chat_history(sk_history)

        return response_text, updated_history
