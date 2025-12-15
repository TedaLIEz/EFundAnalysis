"""KYC Agent that combines chatbot functionality with KYC workflow routing."""

import asyncio
from collections.abc import Generator
import concurrent.futures
import logging

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

    def chat(self, message: str) -> str:
        """Send a message to the agent and get a response.

        Args:
            message: The user's message

        Returns:
            The agent's response as a string

        """
        if not message or not message.strip():
            return "Please provide a valid message."

        # Detect intent
        intent = self._detect_intent(message)

        if intent == "kyc_workflow":
            # Save user message to memory manually for KYC workflow
            user_msg = ChatMessage(role=MessageRole.USER, content=message)
            self.chatbot.memory.put(user_msg)
            # Route to KYC workflow
            try:
                return self._run_kyc_workflow(message)
            except Exception as e:
                logger.exception("Error running KYC workflow")
                return f"An error occurred while processing your KYC request: {str(e)}"
        else:
            # Use normal chatbot (it automatically saves messages to memory)
            try:
                return self.chatbot.chat(message)
            except Exception as e:
                logger.exception("Error in chatbot")
                return f"An error occurred while processing your message: {str(e)}"

    def _run_kyc_workflow(self, user_input: str) -> str:
        """Run KYC workflow synchronously and return the result.

        Args:
            user_input: The user's input message

        Returns:
            The workflow result as a string

        """
        # Create workflow instance if not exists
        if self.kyc_workflow is None:
            self.kyc_workflow = KYCWorkflow(timeout=120, verbose=False)

        # Capture workflow reference for type narrowing
        workflow = self.kyc_workflow

        # Run workflow in async context
        async def run_workflow() -> str:
            handler = workflow.run(user_input=user_input, customer_id=self.customer_id)
            result_text = ""

            async for event in handler.stream_events():
                if isinstance(event, StreamingChunkEvent):
                    if event.chunk:
                        result_text += event.chunk
                elif isinstance(event, StopEvent) and hasattr(event, "result") and isinstance(event.result, dict):
                    # Extract recommendation from result
                    recommendation = event.result.get("recommendation", "")
                    result_text = recommendation if recommendation else str(event.result)

            return result_text if result_text else "KYC workflow completed successfully."

        # Run async workflow synchronously using asyncio.run()
        try:
            result = asyncio.run(run_workflow())
            # Save workflow response to memory
            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=result)
            self.chatbot.memory.put(assistant_msg)
            return result
        except RuntimeError:
            # If event loop already exists, use a thread to run async code
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, run_workflow())
                result = future.result()
            # Save workflow response to memory
            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=result)
            self.chatbot.memory.put(assistant_msg)
            return result

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

    def _stream_kyc_workflow(self, user_input: str) -> Generator[str, None]:
        """Stream KYC workflow results.

        Args:
            user_input: The user's input message

        Yields:
            Response chunks as strings

        """
        # Create workflow instance if not exists
        if self.kyc_workflow is None:
            self.kyc_workflow = KYCWorkflow(timeout=120, verbose=False)

        # Capture workflow reference for type narrowing
        workflow = self.kyc_workflow

        # Run workflow in async context
        async def collect_chunks() -> str:
            handler = workflow.run(user_input=user_input, customer_id=self.customer_id)
            full_response = ""

            async for event in handler.stream_events():
                if isinstance(event, StreamingChunkEvent):
                    if event.chunk:
                        full_response += event.chunk
                elif (
                    isinstance(event, StopEvent)
                    and not full_response
                    and hasattr(event, "result")
                    and isinstance(event.result, dict)
                ):
                    # Extract recommendation from result if no chunks were collected
                    recommendation = event.result.get("recommendation", "")
                    if recommendation:
                        full_response = recommendation

            return full_response

        # Run async workflow synchronously
        try:
            full_response = asyncio.run(collect_chunks())
        except RuntimeError:
            # If event loop already exists, use a thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, collect_chunks())
                full_response = future.result()

        # Yield response character by character to simulate streaming
        yield from full_response
        # Save full response to memory
        if full_response:
            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
            self.chatbot.memory.put(assistant_msg)

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
