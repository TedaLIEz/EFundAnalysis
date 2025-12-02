"""Integration tests for the Chatbot class."""

import asyncio

from core.llm.chat.chatbot import Chatbot

async def test_stream_chat():
    """Test the async streaming chat functionality."""
    chatbot = Chatbot()
    for chunk in chatbot.stream_chat("How are you?"):
        print(f"Stream response: {chunk}")

if __name__ == "__main__":
    asyncio.run(test_stream_chat())
