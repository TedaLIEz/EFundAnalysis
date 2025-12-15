"""Integration tests for the Chatbot class."""

import asyncio
import logging
# Fallback if package import fails
from tests.integration.test_utils import setup_logging
from core.llm.chat.chatbot import Chatbot
from core.llm.prompt.prompt_loader import PromptLoader
setup_logging()
logger = logging.getLogger(__name__)


def test_stream_chat():
    """Test synchronous streaming chat functionality."""
    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    chatbot = Chatbot(system_prompt=system_prompt)

    question = "我是一个风险厌恶的投资者，我希望投资10000元，并持有5年，我应该如何分配资产？"
    logger.info(f"Testing stream_chat with question: {question[:50]}...")

    print(f"\nUser: {question}")
    print("Chatbot (streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in chatbot.stream_chat(question):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")

    # Verify streaming worked
    full_response = "".join(response_chunks)
    assert len(full_response) > 0, "Streaming should produce a response"
    logger.info(f"Received response of length: {len(full_response)} characters")

    # Verify memory was updated
    history = chatbot.get_chat_history()
    assert len(history) >= 2, "Memory should contain at least 2 messages (1 user + 1 assistant)"


async def test_astream_chat():
    """Test asynchronous streaming chat functionality."""
    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    chatbot = Chatbot(system_prompt=system_prompt)

    question = "我是一个风险厌恶的投资者，我希望投资10000元，并持有5年，我应该如何分配资产？"
    logger.info(f"Testing astream_chat with question: {question[:50]}...")

    print(f"\nUser: {question}")
    print("Chatbot (async streaming): ", end="", flush=True)
    response_chunks = []
    async for token in chatbot.astream_chat(question):
        print(token, end="", flush=True)
        response_chunks.append(token)
    print("\n")

    # Verify streaming worked
    full_response = "".join(response_chunks)
    assert len(full_response) > 0, "Async streaming should produce a response"
    logger.info(f"Received response of length: {len(full_response)} characters")

    # Verify memory was updated
    history = chatbot.get_chat_history()
    assert len(history) >= 2, "Memory should contain at least 2 messages (1 user + 1 assistant)"


def test_chat_history():
    """Test chat history functionality."""
    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    chatbot = Chatbot(system_prompt=system_prompt)

    # Initial history should be empty
    history = chatbot.get_chat_history()
    assert len(history) == 0, "Initial chat history should be empty"

    # Send a message via streaming
    question = "什么是股票？"
    _ = "".join(chatbot.stream_chat(question))

    # Verify history was updated
    history = chatbot.get_chat_history()
    assert len(history) >= 2, "History should contain at least 2 messages after chat"
    assert history[0]["role"] == "user", "First message should be from user"
    assert history[1]["role"] == "assistant", "Second message should be from assistant"


def test_reset():
    """Test reset functionality."""
    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    chatbot = Chatbot(system_prompt=system_prompt)

    # Add some conversation
    _ = "".join(chatbot.stream_chat("什么是股票？"))
    _ = "".join(chatbot.stream_chat("什么是基金？"))

    # Verify history before reset
    history_before = chatbot.get_chat_history()
    assert len(history_before) >= 4, "Should have at least 4 messages before reset"

    # Reset
    chatbot.reset()

    # Verify history after reset
    history_after = chatbot.get_chat_history()
    assert len(history_after) == 0, "History should be empty after reset"
