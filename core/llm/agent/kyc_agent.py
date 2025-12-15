"""KYC Agent that combines chatbot functionality with KYC workflow routing."""

import asyncio
from collections.abc import AsyncGenerator, Generator
import logging
import queue
import threading

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.workflow import StopEvent

from core.kyc.workflows.kyc_workflow import KYCWorkflow, StreamingChunkEvent
from core.llm.chat.chatbot import Chatbot
from core.llm.model import create_llm
from core.llm.prompt.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class KYCAgent:
    """Agent that combines chatbot functionality with KYC workflow routing.

    This agent can:
    1. Handle user input to generate responses via LLM
    2. Route to KYC workflow when user asks about personal asset allocation
    3. Maintain conversation memory for both normal chat and workflow interactions
    """

    def __init__(
        self,
        llm: FunctionCallingLLM | None = None,
        system_prompt: str | None = None,
        customer_id: str | None = None,
    ):
        """Initialize the KYC agent.

        Args:
            llm: Optional FunctionCallingLLM instance. If not provided, one will be created
                using environment variables.
            system_prompt: Optional system prompt for the chatbot.
            customer_id: Optional customer ID for KYC workflow tracking.

        """
        self.llm = llm or create_llm()
        self.customer_id = customer_id
        self.chatbot = Chatbot(llm=self.llm, system_prompt=system_prompt)
        self.kyc_workflow: KYCWorkflow | None = None
        self.prompt_loader = PromptLoader()

    def _detect_intent(self, user_input: str) -> str:
        """Detect if user input is about personal asset allocation.

        Args:
            user_input: The user's input message

        Returns:
            "kyc_workflow" if user is asking about personal asset allocation,
            "normal_chat" otherwise

        """
        if not user_input or not user_input.strip():
            return "normal_chat"

        try:
            # Use LLM to classify intent
            prompt = self.prompt_loader.load_prompt_with_context("intent_detection.liquid", {"user_input": user_input})
            response = self.llm.complete(prompt)
            intent = str(response).strip().lower()

            # Normalize response
            if "kyc" in intent or "workflow" in intent:
                return "kyc_workflow"
            return "normal_chat"
        except Exception as e:
            logger.exception("Error detecting intent, defaulting to normal_chat")
            return "normal_chat"

    def stream_chat(self, message: str) -> Generator[str, None]:
        """Stream a response from the agent.

        Args:
            message: The user's message

        Yields:
            Response tokens as strings

        """
        if not message or not message.strip():
            yield "Please provide a valid message."
            return

        # Detect intent
        intent = self._detect_intent(message)

        if intent == "kyc_workflow":
            # Save user message to memory manually for KYC workflow
            user_msg = ChatMessage(role=MessageRole.USER, content=message)
            self.chatbot.memory.put(user_msg)
            # Route to KYC workflow streaming
            try:
                yield from self._stream_kyc_workflow(message)
            except Exception as e:
                logger.exception("Error streaming KYC workflow")
                yield f"An error occurred while processing your KYC request: {str(e)}"
        else:
            # Use normal chatbot streaming (it automatically saves messages to memory)
            try:
                yield from self.chatbot.stream_chat(message)
            except Exception as e:
                logger.exception("Error in chatbot streaming")
                yield f"An error occurred while processing your message: {str(e)}"

    async def astream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Stream a response from the agent asynchronously.

        Args:
            message: The user's message

        Yields:
            Response tokens as strings (yielded asynchronously)

        """
        if not message or not message.strip():
            yield "Please provide a valid message."
            return

        # Detect intent
        intent = self._detect_intent(message)

        if intent == "kyc_workflow":
            # Save user message to memory manually for KYC workflow
            user_msg = ChatMessage(role=MessageRole.USER, content=message)
            self.chatbot.memory.put(user_msg)
            # Route to KYC workflow async streaming
            try:
                async for chunk in self._stream_kyc_workflow_async(message):
                    yield chunk
            except Exception as e:
                logger.exception("Error streaming KYC workflow")
                yield f"An error occurred while processing your KYC request: {str(e)}"
        else:
            # Use normal chatbot async streaming (it automatically saves messages to memory)
            try:
                async for chunk in self.chatbot.astream_chat(message):
                    yield chunk
            except Exception as e:
                logger.exception("Error in chatbot async streaming")
                yield f"An error occurred while processing your message: {str(e)}"

    async def _stream_kyc_workflow_async(self, user_input: str) -> AsyncGenerator[str, None]:
        """Stream KYC workflow results in real-time as chunks arrive (async version).

        Args:
            user_input: The user's input message

        Yields:
            Response chunks as strings (yielded as they arrive from the workflow)

        """
        # Create workflow instance if not exists
        if self.kyc_workflow is None:
            self.kyc_workflow = KYCWorkflow(timeout=120, verbose=False)

        # Capture workflow reference for type narrowing
        workflow = self.kyc_workflow

        handler = workflow.run(user_input=user_input, customer_id=self.customer_id)
        full_response_parts: list[str] = []
        fallback_result = ""

        try:
            async for event in handler.stream_events():
                if isinstance(event, StreamingChunkEvent):
                    if event.chunk:
                        full_response_parts.append(event.chunk)
                        yield event.chunk
                elif (
                    isinstance(event, StopEvent)
                    and not full_response_parts
                    and hasattr(event, "result")
                    and isinstance(event.result, dict)
                ):
                    # Extract recommendation from result if no chunks were collected
                    recommendation = event.result.get("recommendation", "")
                    if recommendation:
                        fallback_result = recommendation

            # If we have a fallback result but no chunks, yield it
            if fallback_result and not full_response_parts:
                yield fallback_result
                full_response_parts.append(fallback_result)
        except Exception as e:
            logger.exception("Error in async workflow streaming")
            yield f"An error occurred while processing your KYC request: {str(e)}"

        # Save full response to memory
        full_response = "".join(full_response_parts) if full_response_parts else fallback_result
        if full_response:
            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
            self.chatbot.memory.put(assistant_msg)

    def _stream_kyc_workflow(self, user_input: str) -> Generator[str, None]:
        """Stream KYC workflow results in real-time as chunks arrive (sync wrapper).

        This is a synchronous wrapper around the async generator that bridges
        async and sync code using a queue and background thread.

        Args:
            user_input: The user's input message

        Yields:
            Response chunks as strings (yielded as they arrive from the workflow)

        """
        # Use a queue to bridge async generator and sync generator
        chunk_queue: queue.Queue[str | None] = queue.Queue()
        error_occurred: threading.Event = threading.Event()
        error_message: str = ""

        async def consume_async_generator() -> None:
            """Consume the async generator and put chunks into queue."""
            try:
                async for chunk in self._stream_kyc_workflow_async(user_input):
                    chunk_queue.put(chunk)
                chunk_queue.put(None)  # Signal completion
            except Exception as e:
                logger.exception("Error consuming async generator")
                error_occurred.set()
                nonlocal error_message
                error_message = str(e)
                chunk_queue.put(None)

        def run_async_in_thread() -> None:
            """Run async generator in a thread with a clean event loop."""
            try:
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(consume_async_generator())
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            except Exception as e:
                logger.exception("Error in async thread")
                error_occurred.set()
                nonlocal error_message
                error_message = str(e)
                chunk_queue.put(None)

        # Start the async generator in a background thread
        thread = threading.Thread(target=run_async_in_thread, daemon=True)
        thread.start()

        # Yield chunks as they arrive from the queue
        while True:
            try:
                chunk = chunk_queue.get(timeout=300)  # 5 minute timeout
                if chunk is None:
                    # Stream completed
                    break
                yield chunk
            except queue.Empty:
                logger.exception("Timeout waiting for workflow chunks")
                yield "Error: Workflow streaming timed out."
                break

        # Wait for thread to complete
        thread.join(timeout=1)

        # Check for errors
        if error_occurred.is_set():
            yield f"An error occurred: {error_message}"

    def reset(self) -> None:
        """Reset the conversation memory and workflow."""
        self.chatbot.reset()
        self.kyc_workflow = None

    def get_chat_history(self) -> list[dict[str, str]]:
        """Get the current chat history.

        Returns:
            List of dictionaries with 'role' and 'content' keys

        """
        return self.chatbot.get_chat_history()
