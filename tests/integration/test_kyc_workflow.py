"""Integration tests for KYC workflow."""

import asyncio
import logging

from tests.integration.test_utils import setup_logging

from core.kyc.workflows.kyc_workflow import KYCWorkflow, StreamingChunkEvent
from llama_index.core.workflow import StopEvent

setup_logging()
logger = logging.getLogger(__name__)


async def test_kyc_workflow_streaming():
    """Test KYC workflow streaming functionality."""
    logger.info("Testing KYC workflow streaming")

    # Create workflow instance
    # Set verbose=False to avoid duplicate output (we handle streaming ourselves)
    workflow = KYCWorkflow(timeout=120, verbose=False)

    # Sample user input - can be unstructured text or structured data
    user_input = """
    我叫张三，今年35岁，住在北京。我已经结婚了，有一个孩子。
    我在一家科技公司工作，年收入大约50万。
    我想投资50万元，投资期限是10年。我能接受的最大亏损是20%。
    我的投资目标是为退休做准备，同时也希望资产能够增值。
    我比较偏好基金和股票投资，但也需要保持一定的流动性。
    """

    print(f"\nUser input: {user_input[:100]}...")
    print("KYC Workflow (streaming): ", end="", flush=True)

    # Run workflow and stream events
    handler = workflow.run(
        user_input=user_input,
        customer_id="CUST001",
    )

    # Stream events as they occur
    chunks = []
    async for event in handler.stream_events():
        if isinstance(event, StreamingChunkEvent):
            # Stream chunks as they arrive (completion event includes newline)
            if event.chunk:
                print(event.chunk, end="", flush=True)
                chunks.append(event.chunk)
        elif isinstance(event, StopEvent):
            logger.info("Workflow completed with StopEvent")

    print("\n")

    # Verify streaming worked
    full_response = "".join(chunks)
    assert len(full_response) > 0, "KYC workflow should produce streaming chunks"
    logger.info(f"Received {len(chunks)} chunks, total length: {len(full_response)} characters")


async def test_kyc_workflow_with_result():
    """Test KYC workflow with result extraction."""
    logger.info("Testing KYC workflow result extraction")

    workflow = KYCWorkflow(timeout=120, verbose=False)

    user_input = """
    我叫李四，今年30岁，单身，住在上海。
    我在金融行业工作，年收入40万。
    我想投资30万元，投资期限是5年。我能接受的最大亏损是10%。
    我的投资目标是为买房做准备。
    """

    print(f"\nUser input: {user_input[:80]}...")
    print("KYC Workflow: ", end="", flush=True)

    handler = workflow.run(
        user_input=user_input,
        customer_id="CUST002",
    )

    chunks = []
    result = None

    async for event in handler.stream_events():
        if isinstance(event, StreamingChunkEvent):
            if event.chunk:
                print(event.chunk, end="", flush=True)
                chunks.append(event.chunk)
        elif isinstance(event, StopEvent):
            if hasattr(event, "result") and isinstance(event.result, dict):
                result = event.result
                logger.info(f"Workflow completed with result: {list(result.keys())}")

    print("\n")

    # Verify workflow completed
    assert len(chunks) > 0 or result is not None, "Workflow should produce either chunks or result"
    if result:
        assert isinstance(result, dict), "Result should be a dictionary"
        logger.info(f"Workflow result keys: {list(result.keys())}")
