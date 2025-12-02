"""Integration tests for the Chatbot class."""

import asyncio

from core.llm.chat.chatbot import Chatbot
from core.llm.model.siliconflow import create_llm as create_siliconflow_llm
from core.llm.model.aopenai import create_llm as create_aopenai_llm
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine import SimpleChatEngine
async def test_stream_chat():
    """Test the async streaming chat functionality."""
    chatbot = Chatbot()
    async for chunk in chatbot.achat("How are you?"):
        print(f"Stream response: {chunk}")


async def main():
    """Main async function for testing."""
    llm = create_aopenai_llm()
    messages = [ChatMessage(role="user", content="How are you?")]
    response_stream = await llm.astream_chat(messages)
    async for chunk in response_stream:
        print(f"Stream response: {chunk}")


if __name__ == "__main__":
    # asyncio.run(test_stream_chat())
    asyncio.run(main())
