"""Integration tests for the Chatbot class."""

import asyncio

from core.llm.chat.chatbot import Chatbot
from core.llm.prompt.prompt_loader import PromptLoader
from llama_index.core.chat_engine.types import ChatMessage

def test_stream_chat():
    """Test the async streaming chat functionality."""
    prompt_loader = PromptLoader()
    system_prompt = prompt_loader.load_prompt("asset_allocation.liquid")
    chatbot = Chatbot(system_prompt=system_prompt)
    question = "我是一个风险厌恶的投资者，我希望投资10000元，并持有5年，我应该如何分配资产？"
    response = chatbot.chat(question)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_stream_chat()
