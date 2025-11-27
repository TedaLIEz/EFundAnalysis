"""Agent implementation with function calling capabilities using LlamaIndex."""

from collections.abc import Callable
from typing import Any

from llama_index.core.agent import ReActAgent
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.memory import BaseMemory
from llama_index.core.tools import BaseTool, FunctionTool
from pydantic import BaseModel, Field

from core.llm.model import create_llm


class FunctionDescription(BaseModel):
    """Description of a function that can be called by the agent."""

    name: str = Field(..., description="Name of the function")
    description: str = Field(..., description="Description of what the function does")
    parameters: dict[str, Any] = Field(..., description="Parameters required by the function")
    required: list[str] = Field(default_factory=list, description="List of required parameters")


class Agent:
    """AI Agent with function calling capabilities."""

    def __init__(
        self,
        llm: FunctionCallingLLM | None = None,
        memory: BaseMemory | None = None,
        tools: list[Callable] | None = None,
        verbose: bool = True,
    ):
        """Initialize the agent with a SiliconFlow LLM.

        Args:
            llm: Optional FunctionCallingLLM instance. If not provided, one will be created
                using environment variables.
            tools: Optional list of callable tools to add to the agent. If not provided, the agent will be created without any tools.
            verbose: Optional boolean to enable verbose mode. If not provided, the agent will be created in verbose mode.

        """
        self.llm = llm or create_llm()
        self.tools: list[BaseTool] = [] if tools is None else [FunctionTool.from_defaults(fn=tool) for tool in tools]
        self.agent: ReActAgent = ReActAgent.from_tools(tools=self.tools, llm=self.llm, memory=memory, verbose=verbose)

    def run(self, prompt: str) -> str:
        """Run the agent with a given prompt.

        Args:
            prompt: The input prompt for the agent

        Returns:
            The agent's response as a string

        """
        try:
            response = self.agent.chat(prompt)
            return str(response)
        except ValueError as e:
            if "Reached max iterations" in str(e):
                return "I apologize, but I don't have enough information to answer this question accurately. Could you please try rephrasing your question or providing more details?"
            raise e

    def get_registered_functions(self) -> list[FunctionDescription]:
        """Get descriptions of all registered functions."""
        return [
            FunctionDescription(
                name=tool.metadata.name,  # type: ignore
                description=tool.metadata.description,
                parameters=tool.metadata.fn_schema.model_fields,  # type: ignore
                required=[k for k, v in tool.metadata.fn_schema.model_fields.items() if v.is_required],  # type: ignore
            )
            for tool in self.tools
        ]

    @property
    def chat_history(self) -> list[ChatMessage]:
        """Get the chat history."""
        return self.agent.chat_history
