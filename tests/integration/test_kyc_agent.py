"""Integration test for the KYCAgent class."""

import logging

from tests.integration.test_utils import setup_logging

from core.kyc.workflows.kyc_agent import KYCAgent
from core.llm.prompt.prompt_loader import PromptLoader

setup_logging()
logger = logging.getLogger(__name__)


def _collect_stream_response(stream_generator):
    """Helper function to collect streaming response into a single string.

    Args:
        stream_generator: Generator that yields string chunks

    Returns:
        Complete response as a string
    """
    return "".join(stream_generator)



async def test_astream_chat():
    """Test asynchronous streaming chat functionality."""
    logger.info("Testing async streaming chat")
    print("\n" + "=" * 80)
    print("Test 4: Asynchronous Streaming Chat")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST005")

    # Test async streaming normal chat
    question = "请简单介绍一下投资组合理论"
    print(f"\nUser: {question}")
    print("Agent (async streaming): ", end="", flush=True)
    response_chunks = []
    async for chunk in agent.astream_chat(question):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")

    # Verify streaming worked
    full_response = "".join(response_chunks)
    assert len(full_response) > 0, "Async streaming should produce a response"

    # Test async streaming KYC workflow
    kyc_question = "我想投资30万，请给我资产配置建议。"
    print(f"\nUser: {kyc_question}")
    print("Agent (KYC Workflow async streaming): ", end="", flush=True)
    kyc_chunks = []
    async for chunk in agent.astream_chat(kyc_question):
        print(chunk, end="", flush=True)
        kyc_chunks.append(chunk)
    print("\n")

    # Verify streaming worked
    kyc_response = "".join(kyc_chunks)
    assert len(kyc_response) > 0, "KYC workflow async streaming should produce a response"

    # Verify memory
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 4, "Memory should contain at least 4 messages (2 user + 2 assistant)"
    logger.info(f"Async streaming chat history contains {len(history)} messages")


def test_reset():
    """Test reset functionality."""
    logger.info("Testing reset functionality")
    print("\n" + "=" * 80)
    print("Test 5: Reset Functionality")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST006")

    # Add some conversation using streaming
    print("\nAdding conversation messages...")
    _collect_stream_response(agent.stream_chat("什么是股票？"))
    _collect_stream_response(agent.stream_chat("我想投资，请给我建议。"))

    # Check history before reset
    history_before = agent.get_chat_history()
    print(f"History before reset: {len(history_before)} messages")
    assert len(history_before) >= 4, "Should have at least 4 messages before reset"

    # Reset
    agent.reset()

    # Check history after reset
    history_after = agent.get_chat_history()
    print(f"History after reset: {len(history_after)} messages")
    assert len(history_after) == 0, "History should be empty after reset"
    logger.info("Reset functionality verified successfully")
