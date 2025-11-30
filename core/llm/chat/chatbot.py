"""Basic chatbot implementation using LlamaIndex."""

import logging

from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import ChatMemoryBuffer

from core.llm.model import create_llm

logger = logging.getLogger(__name__)


class Chatbot:
    """Basic chatbot with conversation memory."""

    def __init__(self, llm: FunctionCallingLLM | None = None):
        """Initialize the chatbot with a SiliconFlow LLM.

        Args:
            llm: Optional FunctionCallingLLM instance. If not provided, one will be created
                using environment variables.

        """
        self.llm = llm or create_llm()
        self.memory = ChatMemoryBuffer.from_defaults()
        self.chat_engine = SimpleChatEngine.from_defaults(llm=self.llm, memory=self.memory)

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
            response = self.chat_engine.chat(message)
            logger.info(f"Return response length: {len(str(response))}")
            return str(response)
        except Exception as e:
            return f"An error occurred while processing your message: {str(e)}"

    def reset(self) -> None:
        """Reset the conversation memory."""
        self.memory = ChatMemoryBuffer.from_defaults()
        self.chat_engine = SimpleChatEngine.from_defaults(llm=self.llm, memory=self.memory)

    def get_chat_history(self) -> list[dict[str, str]]:
        """Get the current chat history.

        Returns:
            List of dictionaries with 'role' and 'content' keys

        """
        return [
            {"role": msg.role.value, "content": msg.content}  # type: ignore
            for msg in self.memory.get_all()
        ]
