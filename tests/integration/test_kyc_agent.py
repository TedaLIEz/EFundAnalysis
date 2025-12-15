"""Integration test for the KYCAgent class."""

import logging

from tests.integration.test_utils import setup_logging

from core.llm.agent import KYCAgent
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


async def _collect_astream_response(async_stream_generator):
    """Helper function to collect async streaming response into a single string.

    Args:
        async_stream_generator: AsyncGenerator that yields string chunks

    Returns:
        Complete response as a string
    """
    chunks = []
    async for chunk in async_stream_generator:
        chunks.append(chunk)
    return "".join(chunks)


def test_normal_chat():
    """Test normal chat functionality (non-KYC questions)."""
    logger.info("Testing normal chat functionality")
    print("\n" + "=" * 80)
    print("Test 1: Normal Chat (Non-KYC Questions)")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST001")

    # Test general financial question
    question1 = "什么是股票？"
    print(f"\nUser: {question1}")
    print("Agent (streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in agent.stream_chat(question1):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")
    response1 = "".join(response_chunks)
    print(f"Agent (full response): {response1[:200]}...")  # Print first 200 chars

    # Test market question
    question2 = "请介绍一下当前市场行情"
    print(f"\nUser: {question2}")
    print("Agent (streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in agent.stream_chat(question2):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")
    response2 = "".join(response_chunks)
    print(f"Agent (full response): {response2[:200]}...")

    # Verify memory
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 4, "Memory should contain at least 4 messages (2 user + 2 assistant)"
    logger.info(f"Chat history contains {len(history)} messages")


def test_kyc_workflow_routing():
    """Test KYC workflow routing for asset allocation questions."""
    logger.info("Testing KYC workflow routing")
    print("\n" + "=" * 80)
    print("Test 2: KYC Workflow Routing (Asset Allocation Questions)")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST002")

    # Test KYC workflow trigger
    kyc_question = """
    我叫李四，今年35岁，住在上海。我已经结婚了，有一个孩子。
    我在一家金融公司工作，年收入大约60万。
    我想投资80万元，投资期限是8年。我能接受的最大亏损是15%。
    我的投资目标是为孩子教育做准备，同时也希望资产能够增值。
    我比较偏好基金和股票投资，但也需要保持一定的流动性。
    请给我个人资产配置建议。
    """
    print(f"\nUser: {kyc_question[:100]}...")
    print("\nAgent (KYC Workflow streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in agent.stream_chat(kyc_question):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")
    response = "".join(response_chunks)
    print(f"\nFull response length: {len(response)} characters")

    # Verify memory
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 2, "Memory should contain at least 2 messages (1 user + 1 assistant)"
    assert len(response) > 0, "KYC workflow should produce a response"
    logger.info(f"KYC workflow response length: {len(response)} characters")


def test_mixed_conversation():
    """Test mixed conversation with both normal chat and KYC workflow."""
    logger.info("Testing mixed conversation")
    print("\n" + "=" * 80)
    print("Test 3: Mixed Conversation (Normal Chat + KYC Workflow)")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST003")

    # Start with normal question
    question1 = "什么是资产配置？"
    print(f"\nUser: {question1}")
    print("Agent (streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in agent.stream_chat(question1):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")
    response1 = "".join(response_chunks)
    print(f"Agent (full response): {response1[:150]}...")

    # Then ask for personal advice (should trigger KYC workflow)
    question2 = "我想投资50万元，请根据我的情况给我资产配置建议。我今年30岁，年收入40万，风险承受能力中等。"
    print(f"\nUser: {question2}")
    print("Agent (KYC Workflow streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in agent.stream_chat(question2):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")
    response2 = "".join(response_chunks)
    print(f"Agent (full response): {response2[:500] + '...' if len(response2) > 500 else response2}")

    # Verify memory contains both conversations
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 4, "Memory should contain at least 4 messages (2 user + 2 assistant)"
    logger.info(f"Mixed conversation history contains {len(history)} messages")


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
