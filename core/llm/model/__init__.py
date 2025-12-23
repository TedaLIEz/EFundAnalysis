from llama_index.core.llms.function_calling import FunctionCallingLLM

from .factory import LLMFactory, LLMProvider


# Backward compatibility: create_llm() uses the factory with default provider
def create_llm() -> FunctionCallingLLM:
    """Create an LLM instance using the default provider.

    This function maintains backward compatibility. It uses LLMFactory
    with the provider specified by LLM_PROVIDER environment variable
    or defaults to "azure_openai".

    Returns:
        FunctionCallingLLM: Configured LLM instance.

    """
    return LLMFactory.create()


__all__ = ["create_llm", "LLMFactory", "LLMProvider"]
