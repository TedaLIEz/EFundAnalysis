"""
Agent implementation with function calling capabilities using LlamaIndex.
"""

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llm import create_llm

class FunctionDescription(BaseModel):
    """Description of a function that can be called by the agent."""
    name: str = Field(..., description="Name of the function")
    description: str = Field(..., description="Description of what the function does")
    parameters: Dict[str, Any] = Field(..., description="Parameters required by the function")
    required: List[str] = Field(default_factory=list, description="List of required parameters")

class Agent:
    """AI Agent with function calling capabilities."""
    
    def __init__(self, llm: Optional[FunctionCallingLLM] = None):
        """Initialize the agent with a SiliconFlow LLM.
        
        Args:
            llm: Optional FunctionCallingLLM instance. If not provided, one will be created
                using environment variables.
        """
        self.llm = llm or create_llm()
        self.tools: List[FunctionTool] = []
        self.agent = None

    def add_function(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Add a function that the agent can call.
        
        Args:
            func: The function to add
            name: Optional name for the function (defaults to function name)
            description: Optional description of what the function does
        """
        tool = FunctionTool.from_defaults(
            fn=func,
            name=name or func.__name__,
            description=description or func.__doc__ or "No description provided"
        )
        self.tools.append(tool)
        
        # Recreate the agent with updated tools
        self.agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )

    def run(self, prompt: str) -> str:
        """
        Run the agent with a given prompt.
        
        Args:
            prompt: The input prompt for the agent
            
        Returns:
            The agent's response as a string
            
        Raises:
            ValueError: If no functions have been added to the agent
        """
        if not self.agent:
            raise ValueError("No functions have been added to the agent yet")
            
        response = self.agent.chat(prompt)
        return str(response)

    def get_registered_functions(self) -> List[FunctionDescription]:
        """Get descriptions of all registered functions."""
        return [
            FunctionDescription(
                name=tool.metadata.name,
                description=tool.metadata.description,
                parameters=tool.metadata.fn_schema.model_fields,
                required=[k for k, v in tool.metadata.fn_schema.model_fields.items() if v.is_required]
            )
            for tool in self.tools
        ] 