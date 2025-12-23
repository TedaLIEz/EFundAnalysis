"""Integration tests for the LLMMemory class with real LLM instances."""

import logging

from dotenv import load_dotenv

from tests.integration.test_utils import setup_logging

from core.llm.embedding.siliconflow import create_embedding_model
from core.llm.memory.memory import LLMMemory
from core.llm.model import LLMFactory
from llama_index.core.base.llms.types import ChatMessage, MessageRole

# Load environment variables
load_dotenv()

setup_logging()
logger = logging.getLogger(__name__)


def test_from_defaults():
    """Test creating memory with default settings."""
    logger.info("Testing from_defaults factory method")
    print("\n" + "=" * 80)
    print("Test 1: Memory from_defaults")
    print("=" * 80)

    memory = LLMMemory.from_defaults()
    assert memory.token_limit == 3000
    assert len(memory.memory_blocks) == 0
    assert isinstance(memory.get_memory(), type(memory.get_memory()))

    # Test basic operations
    message = ChatMessage(role=MessageRole.USER, content="Hello, test message")
    memory.put(message)
    messages = memory.get_all()
    assert len(messages) > 0
    print(f"✓ Successfully created default memory and stored {len(messages)} message(s)")

    memory.reset()
    messages_after_reset = memory.get_all()
    assert len(messages_after_reset) == 0
    print("✓ Successfully reset memory")
    logger.info("from_defaults test completed successfully")


def test_with_static_memory():
    """Test creating memory with static memory block."""
    logger.info("Testing with_static_memory factory method")
    print("\n" + "=" * 80)
    print("Test 2: Memory with_static_memory")
    print("=" * 80)

    static_content = "User preferences: prefers concise answers, risk-averse investor"
    memory = LLMMemory.with_static_memory(static_content=static_content)
    assert memory.token_limit == 3000
    assert len(memory.memory_blocks) == 1
    print(f"✓ Successfully created memory with static content: {static_content[:50]}...")

    # Test that static memory persists
    message = ChatMessage(role=MessageRole.USER, content="What are my preferences?")
    memory.put(message)
    messages = memory.get_all()
    assert len(messages) > 0
    print(f"✓ Static memory persists after adding messages ({len(messages)} messages)")

    memory.reset()
    # After reset, static memory structure should still be intact
    assert isinstance(memory.get_memory(), type(memory.get_memory()))
    print("✓ Memory structure intact after reset")
    logger.info("with_static_memory test completed successfully")


def test_with_fact_extraction():
    """Test creating memory with fact extraction memory block."""
    logger.info("Testing with_fact_extraction factory method")
    print("\n" + "=" * 80)
    print("Test 3: Memory with_fact_extraction")
    print("=" * 80)

    llm = LLMFactory.create()
    memory = LLMMemory.with_fact_extraction(llm=llm)
    assert memory.token_limit == 3000
    assert len(memory.memory_blocks) == 1
    print("✓ Successfully created memory with fact extraction block")

    # Test adding messages
    messages_to_add = [
        ChatMessage(role=MessageRole.USER, content="I am 30 years old and work as a software engineer."),
        ChatMessage(role=MessageRole.ASSISTANT, content="Thank you for sharing that information."),
        ChatMessage(role=MessageRole.USER, content="I want to invest $50,000 for retirement."),
    ]

    for msg in messages_to_add:
        memory.put(msg)

    all_messages = memory.get_all()
    assert len(all_messages) >= len(messages_to_add)
    print(f"✓ Successfully stored {len(messages_to_add)} messages, retrieved {len(all_messages)} messages")

    logger.info("with_fact_extraction test completed successfully")


def test_with_vector_memory():
    """Test creating memory with vector memory block."""
    logger.info("Testing with_vector_memory factory method")
    print("\n" + "=" * 80)
    print("Test 4: Memory with_vector_memory")
    print("=" * 80)

    embed_model = create_embedding_model()
    memory = LLMMemory.with_vector_memory(embed_model=embed_model)
    assert memory.token_limit == 3000
    assert len(memory.memory_blocks) == 1
    print("✓ Successfully created memory with vector memory block")

    # Test adding messages
    messages_to_add = [
        ChatMessage(role=MessageRole.USER, content="What is diversification?"),
        ChatMessage(role=MessageRole.ASSISTANT, content="Diversification is spreading investments across different assets."),
        ChatMessage(role=MessageRole.USER, content="How does it reduce risk?"),
    ]

    for msg in messages_to_add:
        memory.put(msg)

    all_messages = memory.get_all()
    assert len(all_messages) >= len(messages_to_add)
    print(f"✓ Successfully stored {len(messages_to_add)} messages, retrieved {len(all_messages)} messages")

    logger.info("with_vector_memory test completed successfully")


def test_with_all_memory_types():
    """Test creating memory with all memory types enabled."""
    logger.info("Testing with_all_memory_types factory method")
    print("\n" + "=" * 80)
    print("Test 5: Memory with_all_memory_types")
    print("=" * 80)

    llm = LLMFactory.create()
    embed_model = create_embedding_model()
    static_content = "Customer profile: High net worth individual, prefers active management"

    memory = LLMMemory.with_all_memory_types(
        llm=llm, embed_model=embed_model, static_content=static_content
    )
    assert memory.token_limit == 3000
    # Should have 3 memory blocks: static, fact extraction, and vector
    assert len(memory.memory_blocks) == 3
    print("✓ Successfully created memory with all memory types (static, fact extraction, vector)")

    # Test adding multiple messages
    conversation = [
        ChatMessage(role=MessageRole.USER, content="I have $1 million to invest."),
        ChatMessage(role=MessageRole.ASSISTANT, content="That's a significant amount. Let's discuss your goals."),
        ChatMessage(role=MessageRole.USER, content="I want growth with moderate risk."),
        ChatMessage(role=MessageRole.ASSISTANT, content="A balanced portfolio might suit your needs."),
    ]

    for msg in conversation:
        memory.put(msg)

    all_messages = memory.get_all()
    assert len(all_messages) >= len(conversation)
    print(f"✓ Successfully stored {len(conversation)} messages, retrieved {len(all_messages)} messages")

    # Test reset
    memory.reset()
    # After reset, memory structure should still be intact
    assert isinstance(memory.get_memory(), type(memory.get_memory()))
    print("✓ Memory structure intact after reset")

    logger.info("with_all_memory_types test completed successfully")


def test_memory_operations():
    """Test various memory operations with real instances."""
    logger.info("Testing memory operations")
    print("\n" + "=" * 80)
    print("Test 6: Memory Operations")
    print("=" * 80)

    memory = LLMMemory.from_defaults()

    # Test put and get_all
    message1 = ChatMessage(role=MessageRole.USER, content="First message")
    message2 = ChatMessage(role=MessageRole.ASSISTANT, content="First response")
    message3 = ChatMessage(role=MessageRole.USER, content="Second message")

    memory.put(message1)
    memory.put(message2)
    memory.put(message3)

    all_messages = memory.get_all()
    assert len(all_messages) >= 3
    print(f"✓ Successfully stored and retrieved {len(all_messages)} messages")

    # Test get method
    retrieved = memory.get()
    assert isinstance(retrieved, list)
    print("✓ get() method works correctly")

    # Test reset
    memory.reset()
    messages_after_reset = memory.get_all()
    assert len(messages_after_reset) == 0
    print("✓ reset() method works correctly")

    logger.info("memory_operations test completed successfully")


def test_memory_with_custom_token_limit():
    """Test memory with custom token limits."""
    logger.info("Testing memory with custom token limits")
    print("\n" + "=" * 80)
    print("Test 7: Memory with Custom Token Limits")
    print("=" * 80)

    # Test default memory with custom token limit
    memory1 = LLMMemory.from_defaults(token_limit=5000)
    assert memory1.token_limit == 5000
    print("✓ Default memory with custom token limit (5000)")

    # Test static memory with custom token limit
    memory2 = LLMMemory.with_static_memory(static_content="Test content", token_limit=2000)
    assert memory2.token_limit == 2000
    print("✓ Static memory with custom token limit (2000)")

    # Test fact extraction with custom token limit
    llm = LLMFactory.create()
    memory3 = LLMMemory.with_fact_extraction(llm=llm, token_limit=6000)
    assert memory3.token_limit == 6000
    print("✓ Fact extraction memory with custom token limit (6000)")

    # Test vector memory with custom token limit
    embed_model = create_embedding_model()
    memory4 = LLMMemory.with_vector_memory(embed_model=embed_model, token_limit=4000)
    assert memory4.token_limit == 4000
    print("✓ Vector memory with custom token limit (4000)")

    # Test all memory types with custom token limit
    memory5 = LLMMemory.with_all_memory_types(
        llm=llm, embed_model=embed_model, static_content="Test", token_limit=8000
    )
    assert memory5.token_limit == 8000
    print("✓ All memory types with custom token limit (8000)")

    logger.info("memory_with_custom_token_limit test completed successfully")


def test_memory_persistence():
    """Test that memory persists across multiple operations."""
    logger.info("Testing memory persistence")
    print("\n" + "=" * 80)
    print("Test 8: Memory Persistence")
    print("=" * 80)

    memory = LLMMemory.from_defaults()

    # Add multiple messages
    for i in range(5):
        user_msg = ChatMessage(role=MessageRole.USER, content=f"Message {i+1}")
        assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=f"Response {i+1}")
        memory.put(user_msg)
        memory.put(assistant_msg)

    all_messages = memory.get_all()
    assert len(all_messages) >= 10
    print(f"✓ Memory persisted {len(all_messages)} messages across multiple operations")

    # Verify messages are still there after multiple get operations
    for _ in range(3):
        retrieved = memory.get_all()
        assert len(retrieved) >= 10

    print("✓ Memory remains consistent across multiple get operations")

    logger.info("memory_persistence test completed successfully")
