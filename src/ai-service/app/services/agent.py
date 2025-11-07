"""Multi-agent chat service using Semantic Kernel orchestration."""

import logging
from typing import AsyncGenerator

from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from semantic_kernel import Kernel
from semantic_kernel.agents import (
    ChatCompletionAgent,
    HandoffOrchestration,
    OrchestrationHandoffs,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.utils.finish_reason import FinishReason

from ..core.config import settings
from ..models import ChatHistoryModel, chat_history_to_sk, sk_to_chat_history
from ..plugins import WeatherPlugin

logger = logging.getLogger(__name__)


class ChatAgentService:
    """Multi-agent orchestration service using Semantic Kernel."""

    def __init__(self):
        """Initialize multi-agent chat with handoff orchestration."""
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

        # Create kernel for query agent with weather plugin
        query_kernel = Kernel()
        query_kernel.add_service(self.chat_service)
        query_kernel.add_plugin(WeatherPlugin(), plugin_name="weather")

        # Get execution settings with function calling enabled
        query_settings = query_kernel.get_prompt_execution_settings_from_service_id(
            service_id=settings.azure_ai_model_deployment
        )
        from semantic_kernel.connectors.ai import FunctionChoiceBehavior

        query_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Create query agent with weather tool access
        from semantic_kernel.functions import KernelArguments

        self.query_agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=query_kernel,
            name="QueryAgent",
            instructions=(
                "You are a query specialist agent that handles "
                "weather information requests. "
                "Use the weather tool to get current weather data "
                "for any location the user asks about. "
                "Provide clear, factual responses based on the "
                "weather tool results. "
                "When you have completed the weather query, use "
                "complete_task to end with a summary."
            ),
            arguments=KernelArguments(settings=query_settings),
        )

        # Create coordinator agent
        coordinator_kernel = Kernel()
        coordinator_kernel.add_service(self.chat_service)

        # Get execution settings with function calling enabled
        coordinator_settings = (
            coordinator_kernel.get_prompt_execution_settings_from_service_id(
                service_id=settings.azure_ai_model_deployment
            )
        )
        coordinator_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        self.coordinator_agent = ChatCompletionAgent(
            service=self.chat_service,
            kernel=coordinator_kernel,
            name="CoordinatorAgent",
            instructions=(
                "You are a helpful AI assistant that coordinates "
                "user requests. "
                "When users ask about weather information, transfer "
                "to the QueryAgent using the transfer_to_QueryAgent function. "
                "For general conversation, respond directly with "
                "friendly, helpful answers and use complete_task "
                "to end the conversation with a summary."
            ),
            arguments=KernelArguments(settings=coordinator_settings),
        )

        # Define handoff relationships using OrchestrationHandoffs
        # CoordinatorAgent can handoff to QueryAgent
        # QueryAgent can handoff back to CoordinatorAgent
        self.handoffs = (
            OrchestrationHandoffs()
            .add(
                self.coordinator_agent,
                self.query_agent,
                description="Transfer to QueryAgent for weather inquiries",
            )
            .add(
                self.query_agent,
                self.coordinator_agent,
                description="Transfer back to CoordinatorAgent",
            )
        )

        # Create the handoff orchestration (streaming callback set per request)
        self.orchestration_template = {
            "members": [self.coordinator_agent, self.query_agent],
            "handoffs": self.handoffs,
        }

        # Create and start runtime
        self.runtime = InProcessRuntime()
        self.runtime.start()

        # System message for chat history initialization
        self.system_message = (
            "You are a helpful AI assistant with access to "
            "specialized agents for specific tasks like weather queries."
        )

    async def stream_chat_completion(
        self,
        user_message: str,
        chat_history: ChatHistoryModel | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion using handoff orchestration.

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

        # Prepare task with history and current message
        messages = []
        for msg in sk_history.messages:
            messages.append(msg)

        logger.info("Starting handoff orchestration for: %s", user_message)

        # Use asyncio.Queue for thread-safe chunk passing
        import asyncio

        chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()

        async def streaming_callback(
            chunk: object, _is_final: bool
        ) -> None:  # StreamingChatMessageContent
            """Callback to handle streaming chunks."""
            # Import inside to avoid circular dependency issues
            from semantic_kernel.contents import StreamingChatMessageContent

            logger.debug(
                "Streaming callback invoked: chunk_type=%s, is_final=%s",
                type(chunk).__name__,
                _is_final,
            )

            if isinstance(chunk, StreamingChatMessageContent):
                # Extract text content and put in queue
                if hasattr(chunk, "content") and chunk.content:
                    logger.debug("Queueing chunk: %r", chunk.content)
                    await chunk_queue.put(chunk.content)
                else:
                    logger.debug("Chunk has no content: %s", chunk)

        # Create orchestration with streaming callback
        orchestration = HandoffOrchestration(
            members=self.orchestration_template["members"],
            handoffs=self.orchestration_template["handoffs"],
            streaming_agent_response_callback=streaming_callback,
        )

        # Start orchestration in background task
        async def run_orchestration():
            try:
                logger.info("Starting orchestration invoke")
                orchestration_result = await orchestration.invoke(
                    task=messages,
                    runtime=self.runtime,
                )
                logger.info("Waiting for orchestration to complete")
                # Wait for completion
                result = await orchestration_result.get(timeout=60)
                logger.info(
                    "Orchestration complete, result type: %s",
                    type(result).__name__,
                )

                # Fallback streaming if no native chunks
                if chunk_queue.empty():
                    logger.info("No streaming chunks; using fallback word streaming")
                    from semantic_kernel.contents import ChatMessageContent

                    if isinstance(result, ChatMessageContent):
                        text = result.content or ""
                    elif isinstance(result, list):
                        text = " ".join(
                            str(m.content)
                            for m in result
                            if hasattr(m, "content") and m.content
                        )
                    else:
                        text = str(result)

                    # Push word-sized chunks (granularity adjustable)
                    for i, word in enumerate(text.split()):
                        # Prefix space except first word to preserve spacing
                        await chunk_queue.put((" " + word) if i else word)
            except Exception as e:
                logger.error("Orchestration error: %s", e, exc_info=True)
                raise
            finally:
                # Signal completion by putting None in queue
                logger.info("Signaling stream completion")
                await chunk_queue.put(None)

        # Create background task
        orchestration_task = asyncio.create_task(run_orchestration())

        try:
            # Yield chunks as they arrive
            logger.info("Starting to yield chunks from queue")
            chunk_count = 0
            while True:
                chunk = await chunk_queue.get()
                if chunk is None:
                    # Orchestration complete
                    logger.info(
                        "Received completion signal, yielded %d chunks",
                        chunk_count,
                    )
                    break
                chunk_count += 1
                logger.debug("Yielding chunk %d: %r", chunk_count, chunk)
                yield chunk
        finally:
            # Ensure task is cleaned up
            if not orchestration_task.done():
                orchestration_task.cancel()
                try:
                    await orchestration_task
                except asyncio.CancelledError:
                    pass

    async def get_chat_completion(
        self,
        user_message: str,
        chat_history: ChatHistoryModel | None = None,
    ) -> tuple[str, ChatHistoryModel]:
        """
        Get non-streaming chat completion using handoff orchestration.

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

        # Prepare task with history and current message
        messages = []
        for msg in sk_history.messages:
            messages.append(msg)

        logger.info("Invoking handoff orchestration for: %s", user_message)

        # Create orchestration without streaming callback
        orchestration = HandoffOrchestration(
            members=self.orchestration_template["members"],
            handoffs=self.orchestration_template["handoffs"],
        )

        # Invoke orchestration
        orchestration_result = await orchestration.invoke(
            task=messages,
            runtime=self.runtime,
        )

        # Get the result
        result = await orchestration_result.get(timeout=60)

        # Extract response text
        if isinstance(result, ChatMessageContent):
            response_text = result.content or ""
            # Check for content filter
            if (
                hasattr(result, "finish_reason")
                and result.finish_reason == FinishReason.CONTENT_FILTER
            ):
                logger.warning("Chat blocked by content filter")
                if not response_text:
                    response_text = (
                        "I'm sorry, but I can't help with that "
                        "request. It may involve content that "
                        "cannot be shared."
                    )
        elif isinstance(result, list):
            response_text = " ".join(
                str(msg.content) for msg in result if hasattr(msg, "content")
            )
        else:
            response_text = str(result)

        # Add response to history
        if response_text:
            sk_history.add_assistant_message(response_text)

        # Convert back to API model
        updated_history = sk_to_chat_history(sk_history)

        return response_text, updated_history
