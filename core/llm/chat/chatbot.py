"""Basic chatbot implementation using LlamaIndex."""

from collections.abc import AsyncGenerator, Generator
import logging
from typing import TYPE_CHECKING

from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import BaseMemory, Memory

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import AgentChatResponse, StreamingAgentChatResponse

from core.llm.model import LLMFactory

logger = logging.getLogger(__name__)


class Chatbot:
    """Basic chatbot with conversation memory."""

    def __init__(
        self,
        llm: FunctionCallingLLM | None = None,
        memory: BaseMemory | None = None,
        system_prompt: str | None = None,
    ):
        """Initialize the chatbot with an LLM.

        Args:
            llm: Optional FunctionCallingLLM instance. If not provided, one will be created
                using the LLMFactory with the provider specified by LLM_PROVIDER environment variable.
            memory: Optional Memory instance. If not provided, one will be created
                using ChatMemoryBuffer.from_defaults().
            system_prompt: Optional system prompt for the chatbot.
                If not provided, the chatbot will use the default system prompt.

        """
        self.llm = llm or LLMFactory.create()
        self.memory = memory or Memory.from_defaults()
        self.chat_engine = SimpleChatEngine.from_defaults(llm=self.llm, system_prompt=system_prompt, memory=self.memory)

    def stream_chat(self, message: str) -> Generator[str, None]:
        try:
            streaming_response: StreamingAgentChatResponse = self.chat_engine.stream_chat(message)

            # Use async_response_gen() instead of directly consuming achat_stream
            # This avoids the "asynchronous generator is already running" error
            # because the background task consumes achat_stream and puts deltas in a queue
            # async_response_gen() also handles None values properly
            # FIXME: siliconflow is not supporting streaming chat.
            for token in streaming_response.response_gen:
                if token:
                    yield token

        except Exception as e:
            logger.exception("Error in async chat")
            yield f"An error occurred while processing your message: {str(e)}"

    async def astream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Stream a response from the chatbot asynchronously.

        Args:
            message: The user's message

        Yields:
            Response tokens as strings

        """
        try:
            streaming_response: StreamingAgentChatResponse = await self.chat_engine.astream_chat(message)
            async for token in streaming_response.async_response_gen():
                if token:
                    yield token
        except Exception as e:
            logger.exception("Error in async chat")
            yield f"An error occurred while processing your message: {str(e)}"

    def chat(self, message: str) -> str:
        """Send a message to the chatbot and get a response.

        Args:
            message: The user's message

        Returns:
            The chatbot's response as a string

        """
        if not message or not message.strip():
            return "Please provide a valid message."

        try:
            response: AgentChatResponse = self.chat_engine.chat(message)
            logger.info(f"Return response length: {len(str(response))}")
            return str(response)
        except Exception as e:
            return f"An error occurred while processing your message: {str(e)}"

    def reset(self) -> None:
        """Reset the conversation memory."""
        self.memory.reset()

    def get_chat_history(self) -> list[dict[str, str]]:
        """Get the current chat history.

        Returns:
            List of dictionaries with 'role' and 'content' keys

        """
        return [
            {"role": msg.role.value, "content": msg.content}  # type: ignore
            for msg in self.memory.get_all()
        ]
