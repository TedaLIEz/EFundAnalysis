"""Memory implementation using LlamaIndex's Memory framework."""

import logging
from typing import TYPE_CHECKING

from llama_index.core.memory import BaseMemoryBlock, Memory

if TYPE_CHECKING:
    from llama_index.core.embeddings import BaseEmbedding
    from llama_index.core.llms.function_calling import FunctionCallingLLM

logger = logging.getLogger(__name__)


class LLMMemory:
    """Memory wrapper for LLM using LlamaIndex's Memory framework.

    This class provides a flexible memory system that supports both short-term
    (chat history) and long-term memory blocks for enhanced context retention.

    The underlying Memory instance (accessible via get_memory()) implements
    BaseMemory and can be used directly with LlamaIndex agents and chat engines.
    """

    def __init__(
        self,
        memory_blocks: list[BaseMemoryBlock] | None = None,
        token_limit: int = 3000,
    ):
        """Initialize LLM memory with optional memory blocks.

        Args:
            memory_blocks: Optional list of memory blocks for long-term memory.
                If not provided, only short-term memory (chat history) will be used.
            token_limit: Maximum number of tokens to keep in short-term memory.
                Defaults to 3000.

        """
        self.memory_blocks = memory_blocks or []
        self.token_limit = token_limit
        self._memory = Memory(memory_blocks=self.memory_blocks, token_limit=self.token_limit)

    @classmethod
    def from_defaults(
        cls,
        token_limit: int = 3000,
    ) -> "LLMMemory":
        """Create a memory instance with default settings (short-term only).

        Args:
            token_limit: Maximum number of tokens to keep in short-term memory.
                Defaults to 3000.

        Returns:
            LLMMemory instance with only short-term memory enabled.

        """
        return cls(memory_blocks=None, token_limit=token_limit)

    @classmethod
    def with_static_memory(
        cls,
        static_content: str,
        token_limit: int = 3000,
    ) -> "LLMMemory":
        """Create a memory instance with static memory block.

        Static memory stores fixed information that persists across conversations.

        Args:
            static_content: Static information to store in memory.
            token_limit: Maximum number of tokens to keep in short-term memory.
                Defaults to 3000.

        Returns:
            LLMMemory instance with static memory block.

        """
        from llama_index.core.base.llms.types import TextBlock
        from llama_index.core.memory import StaticMemoryBlock

        # StaticMemoryBlock expects a list of ContentBlock (e.g., TextBlock)
        text_block = TextBlock(text=static_content)
        static_block = StaticMemoryBlock(static_content=[text_block])
        return cls(memory_blocks=[static_block], token_limit=token_limit)

    @classmethod
    def with_fact_extraction(
        cls,
        llm: "FunctionCallingLLM",
        token_limit: int = 3000,
    ) -> "LLMMemory":
        """Create a memory instance with fact extraction memory block.

        Fact extraction memory automatically extracts and stores facts from
        conversation history for long-term retention.

        Args:
            llm: LLM instance used for fact extraction.
            token_limit: Maximum number of tokens to keep in short-term memory.
                Defaults to 3000.

        Returns:
            LLMMemory instance with fact extraction memory block.

        """
        from llama_index.core.memory import FactExtractionMemoryBlock

        fact_block = FactExtractionMemoryBlock(llm=llm)
        return cls(memory_blocks=[fact_block], token_limit=token_limit)

    @classmethod
    def with_vector_memory(
        cls,
        embed_model: "BaseEmbedding",
        token_limit: int = 3000,
    ) -> "LLMMemory":
        """Create a memory instance with vector memory block.

        Vector memory stores and retrieves chat messages from a vector database,
        enabling semantic search over conversation history.

        Args:
            embed_model: Embedding model for vectorizing chat messages.
            token_limit: Maximum number of tokens to keep in short-term memory.
                Defaults to 3000.

        Returns:
            LLMMemory instance with vector memory block.

        """
        from llama_index.core.memory import VectorMemoryBlock
        from llama_index.core.vector_stores import SimpleVectorStore

        # VectorMemoryBlock requires a vector_store parameter
        # FIXME: Value error, vector_store must store text to be used as a retrieval memory block [type=value_error, input_value=SimpleVectorStore(stores_...d={}, metadata_dict={})), input_type=SimpleVectorStore]
        vector_store = SimpleVectorStore()
        vector_block = VectorMemoryBlock(embed_model=embed_model, vector_store=vector_store)
        return cls(memory_blocks=[vector_block], token_limit=token_limit)

    @classmethod
    def with_all_memory_types(
        cls,
        llm: "FunctionCallingLLM",
        embed_model: "BaseEmbedding",
        static_content: str | None = None,
        token_limit: int = 3000,
    ) -> "LLMMemory":
        """Create a memory instance with all memory types enabled.

        This combines static, fact extraction, and vector memory for
        comprehensive context retention.

        Args:
            llm: LLM instance used for fact extraction.
            embed_model: Embedding model for vectorizing chat messages.
            static_content: Optional static information to store in memory.
            token_limit: Maximum number of tokens to keep in short-term memory.
                Defaults to 3000.

        Returns:
            LLMMemory instance with all memory types enabled.

        """
        from llama_index.core.base.llms.types import TextBlock
        from llama_index.core.memory import (
            FactExtractionMemoryBlock,
            StaticMemoryBlock,
            VectorMemoryBlock,
        )
        from llama_index.core.vector_stores import SimpleVectorStore

        memory_blocks: list[BaseMemoryBlock] = []

        if static_content:
            # StaticMemoryBlock expects a list of ContentBlock (e.g., TextBlock)
            text_block = TextBlock(text=static_content)
            static_block = StaticMemoryBlock(static_content=[text_block])
            memory_blocks.append(static_block)

        fact_block = FactExtractionMemoryBlock(llm=llm)
        memory_blocks.append(fact_block)

        # VectorMemoryBlock requires a vector_store parameter
        vector_store = SimpleVectorStore()
        vector_block = VectorMemoryBlock(embed_model=embed_model, vector_store=vector_store)
        memory_blocks.append(vector_block)

        return cls(memory_blocks=memory_blocks, token_limit=token_limit)

    def get_memory(self) -> Memory:
        """Get the underlying Memory instance.

        The returned Memory instance implements BaseMemory and can be used
        directly with LlamaIndex agents and chat engines.

        Returns:
            The Memory instance that implements BaseMemory interface.

        """
        return self._memory

    def reset(self) -> None:
        """Reset the memory, clearing all chat history and memory blocks."""
        self._memory.reset()

    def get_all(self) -> list:
        """Get all messages from memory.

        Returns:
            List of all chat messages in memory.

        """
        return self._memory.get_all()

    def put(self, message) -> None:
        """Add a message to memory.

        Args:
            message: Chat message to add to memory.

        """
        self._memory.put(message)

    def get(self, **kwargs) -> list:
        """Get messages from memory based on query.

        Args:
            **kwargs: Query parameters for retrieving messages.

        Returns:
            List of retrieved messages.

        """
        return self._memory.get(**kwargs)
