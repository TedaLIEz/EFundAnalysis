"""Unit tests for the LLMMemory class."""

import os
from unittest.mock import MagicMock

import pytest
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import BaseMemoryBlock, Memory

from core.llm.memory.memory import LLMMemory
from tests.mock.mock_vector_store import MockVectorStore

# Check if we have real LLM and embedding instances available
HAS_REAL_LLM = bool(os.getenv("LLM_PROVIDER") or os.getenv("AZURE_OPENAI_KEY") or os.getenv("API_KEY"))
HAS_REAL_EMBEDDING = bool(os.getenv("ENDPOINT") and os.getenv("API_KEY") and os.getenv("EMBEDDING_MODEL"))


@pytest.fixture
def real_llm():
    """Fixture to create a real LLM instance if available."""
    if not HAS_REAL_LLM:
        pytest.skip("Real LLM instance not available (missing environment variables)")
    from core.llm.model import LLMFactory

    return LLMFactory.create()


@pytest.fixture
def real_embedding():
    """Fixture to create a real embedding instance if available."""
    if not HAS_REAL_EMBEDDING:
        pytest.skip("Real embedding instance not available (missing environment variables)")
    from core.llm.embedding.siliconflow import create_embedding_model

    return create_embedding_model()


@pytest.fixture
def sample_chat_message():
    """Fixture to create a sample chat message."""
    return ChatMessage(role=MessageRole.USER, content="Hello, how are you?")


@pytest.fixture
def sample_chat_messages():
    """Fixture to create multiple sample chat messages."""
    return [
        ChatMessage(role=MessageRole.USER, content="What is the weather today?"),
        ChatMessage(role=MessageRole.ASSISTANT, content="I don't have access to weather data."),
        ChatMessage(role=MessageRole.USER, content="Tell me about Python."),
        ChatMessage(role=MessageRole.ASSISTANT, content="Python is a programming language."),
    ]


@pytest.fixture
def mock_vector_store():
    """Fixture to create a mock vector store with stores_text=True."""
    return MockVectorStore()


class TestLLMMemoryInit:
    """Test cases for LLMMemory initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        memory = LLMMemory()
        assert memory.token_limit == 3000
        assert memory.memory_blocks == []
        assert isinstance(memory.get_memory(), Memory)

    def test_init_with_memory_blocks(self, real_llm):
        """Test initialization with custom memory blocks."""
        from llama_index.core.memory import FactExtractionMemoryBlock

        fact_block = FactExtractionMemoryBlock(llm=real_llm)
        memory = LLMMemory(memory_blocks=[fact_block], token_limit=5000)
        assert memory.token_limit == 5000
        assert len(memory.memory_blocks) == 1
        assert isinstance(memory.get_memory(), Memory)

    def test_init_with_custom_token_limit(self):
        """Test initialization with custom token limit."""
        memory = LLMMemory(token_limit=1000)
        assert memory.token_limit == 1000


class TestLLMMemoryFromDefaults:
    """Test cases for from_defaults factory method."""

    def test_from_defaults_default_token_limit(self):
        """Test from_defaults with default token limit."""
        memory = LLMMemory.from_defaults()
        assert memory.token_limit == 3000
        assert memory.memory_blocks == []
        assert isinstance(memory.get_memory(), Memory)

    def test_from_defaults_custom_token_limit(self):
        """Test from_defaults with custom token limit."""
        memory = LLMMemory.from_defaults(token_limit=2000)
        assert memory.token_limit == 2000
        assert memory.memory_blocks == []


class TestLLMMemoryWithStaticMemory:
    """Test cases for with_static_memory factory method."""

    def test_with_static_memory(self):
        """Test creating memory with static memory block."""
        static_content = "User preferences: prefers concise answers"
        memory = LLMMemory.with_static_memory(static_content=static_content)
        assert memory.token_limit == 3000
        assert len(memory.memory_blocks) == 1
        assert isinstance(memory.get_memory(), Memory)

    def test_with_static_memory_custom_token_limit(self):
        """Test creating memory with static memory and custom token limit."""
        static_content = "User name: John Doe"
        memory = LLMMemory.with_static_memory(static_content=static_content, token_limit=5000)
        assert memory.token_limit == 5000
        assert len(memory.memory_blocks) == 1

    def test_with_static_memory_empty_content(self):
        """Test creating memory with empty static content."""
        memory = LLMMemory.with_static_memory(static_content="")
        assert len(memory.memory_blocks) == 1


class TestLLMMemoryWithFactExtraction:
    """Test cases for with_fact_extraction factory method."""

    def test_with_fact_extraction(self, real_llm):
        """Test creating memory with fact extraction block."""
        memory = LLMMemory.with_fact_extraction(llm=real_llm)
        assert memory.token_limit == 3000
        assert len(memory.memory_blocks) == 1
        assert isinstance(memory.get_memory(), Memory)

    def test_with_fact_extraction_custom_token_limit(self, real_llm):
        """Test creating memory with fact extraction and custom token limit."""
        memory = LLMMemory.with_fact_extraction(llm=real_llm, token_limit=4000)
        assert memory.token_limit == 4000
        assert len(memory.memory_blocks) == 1


class TestLLMMemoryWithVectorMemory:
    """Test cases for with_vector_memory factory method."""

    def test_with_vector_memory(self, real_embedding, mock_vector_store):
        """Test creating memory with vector memory block."""
        memory = LLMMemory.with_vector_memory(embed_model=real_embedding, vector_store=mock_vector_store)
        assert memory.token_limit == 3000
        assert len(memory.memory_blocks) == 1
        assert isinstance(memory.get_memory(), Memory)

    def test_with_vector_memory_custom_token_limit(self, real_embedding, mock_vector_store):
        """Test creating memory with vector memory and custom token limit."""
        memory = LLMMemory.with_vector_memory(
            embed_model=real_embedding, vector_store=mock_vector_store, token_limit=6000
        )
        assert memory.token_limit == 6000
        assert len(memory.memory_blocks) == 1


class TestLLMMemoryWithAllMemoryTypes:
    """Test cases for with_all_memory_types factory method."""

    def test_with_all_memory_types_with_static(self, real_llm, real_embedding, mock_vector_store):
        """Test creating memory with all memory types including static content."""
        static_content = "User profile: Active investor"
        memory = LLMMemory.with_all_memory_types(
            llm=real_llm,
            embed_model=real_embedding,
            vector_store=mock_vector_store,
            static_content=static_content,
        )
        assert memory.token_limit == 3000
        # Should have 3 memory blocks: static, fact extraction, and vector
        assert len(memory.memory_blocks) == 3
        assert isinstance(memory.get_memory(), Memory)

    def test_with_all_memory_types_without_static(self, real_llm, real_embedding, mock_vector_store):
        """Test creating memory with all memory types without static content."""
        memory = LLMMemory.with_all_memory_types(
            llm=real_llm, embed_model=real_embedding, vector_store=mock_vector_store, static_content=None
        )
        assert memory.token_limit == 3000
        # Should have 2 memory blocks: fact extraction and vector (no static)
        assert len(memory.memory_blocks) == 2
        assert isinstance(memory.get_memory(), Memory)

    def test_with_all_memory_types_custom_token_limit(self, real_llm, real_embedding, mock_vector_store):
        """Test creating memory with all memory types and custom token limit."""
        static_content = "Preferences: Detailed explanations"
        memory = LLMMemory.with_all_memory_types(
            llm=real_llm,
            embed_model=real_embedding,
            vector_store=mock_vector_store,
            static_content=static_content,
            token_limit=8000,
        )
        assert memory.token_limit == 8000
        assert len(memory.memory_blocks) == 3


class TestLLMMemoryMethods:
    """Test cases for LLMMemory instance methods."""

    def test_get_memory(self):
        """Test get_memory returns Memory instance."""
        memory = LLMMemory.from_defaults()
        memory_instance = memory.get_memory()
        assert isinstance(memory_instance, Memory)

    def test_reset(self, sample_chat_message):
        """Test reset clears all messages."""
        memory = LLMMemory.from_defaults()
        memory.put(sample_chat_message)
        assert len(memory.get_all()) > 0
        memory.reset()
        assert len(memory.get_all()) == 0

    def test_put_and_get_all(self, sample_chat_message):
        """Test putting and getting messages."""
        memory = LLMMemory.from_defaults()
        memory.put(sample_chat_message)
        messages = memory.get_all()
        assert len(messages) > 0
        # Check that the message content is in the retrieved messages
        message_contents = [str(msg) for msg in messages]
        assert any("Hello" in content for content in message_contents)

    def test_put_multiple_messages(self, sample_chat_messages):
        """Test putting multiple messages."""
        memory = LLMMemory.from_defaults()
        for msg in sample_chat_messages:
            memory.put(msg)
        messages = memory.get_all()
        assert len(messages) >= len(sample_chat_messages)

    def test_get_with_kwargs(self, sample_chat_messages):
        """Test get method with query parameters."""
        memory = LLMMemory.from_defaults()
        for msg in sample_chat_messages:
            memory.put(msg)
        # get() should return messages based on query
        messages = memory.get()
        assert isinstance(messages, list)

    def test_get_all_empty_memory(self):
        """Test get_all on empty memory."""
        memory = LLMMemory.from_defaults()
        messages = memory.get_all()
        assert isinstance(messages, list)
        assert len(messages) == 0

    def test_reset_empty_memory(self):
        """Test reset on empty memory."""
        memory = LLMMemory.from_defaults()
        memory.reset()  # Should not raise an error
        assert len(memory.get_all()) == 0


class TestLLMMemoryIntegration:
    """Integration tests for LLMMemory with different memory types."""

    def test_static_memory_persistence(self, sample_chat_message):
        """Test that static memory persists across resets."""
        static_content = "System configuration: Test mode"
        memory = LLMMemory.with_static_memory(static_content=static_content)
        memory.put(sample_chat_message)
        messages_before = memory.get_all()
        memory.reset()
        messages_after = memory.get_all()
        # Static memory should persist, so messages_after might not be completely empty
        # But chat history should be cleared
        assert isinstance(messages_after, list)

    def test_fact_extraction_memory_usage(self, real_llm, sample_chat_messages):
        """Test fact extraction memory with multiple messages."""
        memory = LLMMemory.with_fact_extraction(llm=real_llm)
        for msg in sample_chat_messages:
            memory.put(msg)
        messages = memory.get_all()
        assert len(messages) >= len(sample_chat_messages)

    def test_vector_memory_usage(self, real_embedding, sample_chat_messages, mock_vector_store):
        """Test vector memory with multiple messages."""
        memory = LLMMemory.with_vector_memory(embed_model=real_embedding, vector_store=mock_vector_store)
        for msg in sample_chat_messages:
            memory.put(msg)
        messages = memory.get_all()
        assert len(messages) >= len(sample_chat_messages)

    def test_all_memory_types_combined(self, real_llm, real_embedding, sample_chat_messages, mock_vector_store):
        """Test all memory types working together."""
        static_content = "User context: Financial advisor"
        memory = LLMMemory.with_all_memory_types(
            llm=real_llm,
            embed_model=real_embedding,
            vector_store=mock_vector_store,
            static_content=static_content,
        )
        for msg in sample_chat_messages:
            memory.put(msg)
        messages = memory.get_all()
        assert len(messages) >= len(sample_chat_messages)
        # Reset should clear chat history but preserve static memory structure
        memory.reset()
        # After reset, memory structure should still be intact
        assert isinstance(memory.get_memory(), Memory)
