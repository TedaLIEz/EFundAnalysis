"""Example usage of KYC workflow."""

import asyncio
import json
import sys
import logging

from core.kyc.workflows.kyc_workflow import KYCWorkflow, StreamingChunkEvent
from llama_index.core.workflow import StopEvent


async def main():
    """Example: Run KYC workflow with sample customer data."""
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

    # Run workflow and stream events
    handler = workflow.run(
        user_input=user_input,
        customer_id="CUST001",
    )

    # Stream events as they occur

    async for event in handler.stream_events():
        if isinstance(event, StreamingChunkEvent):
            # Stream chunks as they arrive (completion event includes newline)
            if event.chunk:
                print(event.chunk, end="", flush=True)


if __name__ == "__main__":
    # Configure logging to output to console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())
