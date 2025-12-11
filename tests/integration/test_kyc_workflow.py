"""Example usage of KYC workflow."""

import asyncio
import json

from core.kyc.workflows.kyc_workflow import KYCWorkflow


async def main():
    """Example: Run KYC workflow with sample customer data."""
    # Create workflow instance
    workflow = KYCWorkflow(timeout=120, verbose=True)

    # Sample user input - can be unstructured text or structured data
    user_input = """
    我叫张三，今年35岁，住在北京。我已经结婚了，有一个孩子。
    我在一家科技公司工作，年收入大约50万。
    我想投资50万元，投资期限是10年。我能接受的最大亏损是20%。
    我的投资目标是为退休做准备，同时也希望资产能够增值。
    我比较偏好基金和股票投资，但也需要保持一定的流动性。
    """

    # Run workflow
    result = await workflow.run(
        user_input=user_input,
        customer_id="CUST001",
    )

    # Print results
    print("\n" + "=" * 80)
    print("KYC Workflow Results")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
