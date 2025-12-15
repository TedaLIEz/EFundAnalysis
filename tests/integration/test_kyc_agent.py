"""Integration test for the KYCAgent class."""

import logging

from core.llm.agent import KYCAgent
from core.llm.prompt.prompt_loader import PromptLoader


def test_normal_chat():
    """Test normal chat functionality (non-KYC questions)."""
    print("\n" + "=" * 80)
    print("Test 1: Normal Chat (Non-KYC Questions)")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST001")

    # Test general financial question
    question1 = "什么是股票？"
    print(f"\nUser: {question1}")
    response1 = agent.chat(question1)
    print(f"Agent: {response1[:200]}...")  # Print first 200 chars

    # Test market question
    question2 = "请介绍一下当前市场行情"
    print(f"\nUser: {question2}")
    response2 = agent.chat(question2)
    print(f"Agent: {response2[:200]}...")

    # Verify memory
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 4, "Memory should contain at least 4 messages (2 user + 2 assistant)"


def test_kyc_workflow_routing():
    """Test KYC workflow routing for asset allocation questions."""
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
    print("\nAgent (KYC Workflow):")
    response = agent.chat(kyc_question)
    print(response)

    # Verify memory
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 2, "Memory should contain at least 2 messages (1 user + 1 assistant)"


def test_mixed_conversation():
    """Test mixed conversation with both normal chat and KYC workflow."""
    print("\n" + "=" * 80)
    print("Test 3: Mixed Conversation (Normal Chat + KYC Workflow)")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST003")

    # Start with normal question
    question1 = "什么是资产配置？"
    print(f"\nUser: {question1}")
    response1 = agent.chat(question1)
    print(f"Agent: {response1[:150]}...")

    # Then ask for personal advice (should trigger KYC workflow)
    question2 = "我想投资50万元，请根据我的情况给我资产配置建议。我今年30岁，年收入40万，风险承受能力中等。"
    print(f"\nUser: {question2}")
    print("\nAgent (KYC Workflow):")
    response2 = agent.chat(question2)
    print(response2[:500] + "..." if len(response2) > 500 else response2)

    # Verify memory contains both conversations
    history = agent.get_chat_history()
    print(f"\nChat history length: {len(history)} messages")
    assert len(history) >= 4, "Memory should contain at least 4 messages (2 user + 2 assistant)"


def test_stream_chat():
    """Test streaming chat functionality."""
    print("\n" + "=" * 80)
    print("Test 4: Streaming Chat")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST004")

    # Test streaming normal chat
    question = "请简单介绍一下投资组合理论"
    print(f"\nUser: {question}")
    print("Agent (streaming): ", end="", flush=True)
    response_chunks = []
    for chunk in agent.stream_chat(question):
        print(chunk, end="", flush=True)
        response_chunks.append(chunk)
    print("\n")

    # Verify streaming worked
    full_response = "".join(response_chunks)
    assert len(full_response) > 0, "Streaming should produce a response"

    # Test streaming KYC workflow
    kyc_question = "我想投资30万，请给我资产配置建议。"
    print(f"\nUser: {kyc_question}")
    print("Agent (KYC Workflow streaming): ", end="", flush=True)
    kyc_chunks = []
    for chunk in agent.stream_chat(kyc_question):
        print(chunk, end="", flush=True)
        kyc_chunks.append(chunk)
    print("\n")

    # Verify streaming worked
    kyc_response = "".join(kyc_chunks)
    assert len(kyc_response) > 0, "KYC workflow streaming should produce a response"


def test_reset():
    """Test reset functionality."""
    print("\n" + "=" * 80)
    print("Test 5: Reset Functionality")
    print("=" * 80)

    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    agent = KYCAgent(system_prompt=system_prompt, customer_id="TEST005")

    # Add some conversation
    agent.chat("什么是股票？")
    agent.chat("我想投资，请给我建议。")

    # Check history before reset
    history_before = agent.get_chat_history()
    print(f"History before reset: {len(history_before)} messages")

    # Reset
    agent.reset()

    # Check history after reset
    history_after = agent.get_chat_history()
    print(f"History after reset: {len(history_after)} messages")
    assert len(history_after) == 0, "History should be empty after reset"


def main():
    """Run all integration tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print("\n" + "=" * 80)
    print("KYC Agent Integration Tests")
    print("=" * 80)

    try:
        test_normal_chat()
        test_kyc_workflow_routing()
        test_mixed_conversation()
        test_stream_chat()
        test_reset()

        print("\n" + "=" * 80)
        print("All tests completed successfully!")
        print("=" * 80)
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        logging.exception("Test failure")
        raise


if __name__ == "__main__":
    main()
