"""
Example usage of the Agent class with function calling capabilities.
"""

import asyncio
from typing import Dict
from agent import Agent

def calculate_sum(a: float, b: float) -> float:
    """Calculate the sum of two numbers."""
    return a + b

def get_weather(city: str) -> Dict[str, str]:
    """Get the weather for a given city (mock function)."""
    return {
        "temperature": "25°C",
        "condition": "sunny"
    }

def main():
    # Create an agent
    agent = Agent()
    
    # Add some functions that the agent can use
    agent.add_function(calculate_sum)
    agent.add_function(get_weather)
    
    # List available functions
    functions = agent.get_registered_functions()
    print("Available functions:")
    for func in functions:
        print(f"- {func.name}: {func.description}")
        print(f"  Parameters: {func.parameters}")
        print(f"  Required: {func.required}")
        print()
    
    # Run the agent with a prompt
    prompt = "What's the sum of 5 and 3, and what's the weather in London?"
    response = agent.run(prompt)
    print(f"\nPrompt: {prompt}")
    print(f"Response: {response}")

if __name__ == "__main__":
    main()