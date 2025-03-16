"""
LLM configuration module for setting up the language model with SiliconFlow provider.
"""

import os
from dotenv import load_dotenv
from llama_index.llms.siliconflow import SiliconFlow
from llama_index.core.llms.function_calling import FunctionCallingLLM
load_dotenv()

def create_llm() -> FunctionCallingLLM:
    """Create and return a configured SiliconFlow LLM instance.
    
    Returns:
        SiliconFlow: Configured LLM instance using environment variables
        
    Raises:
        ValueError: If required environment variables are missing
    """
    endpoint = os.getenv("ENDPOINT")
    api_key = os.getenv("API_KEY")
    model = os.getenv("LLM_MODEL")
    
    if not all([endpoint, api_key, model]):
        raise ValueError("Missing required environment variables: ENDPOINT, API_KEY, or LLM_MODEL")
    
    return SiliconFlow(
        api_base=endpoint,
        api_key=api_key,
        model=model,
        temperature=0,
    ) 