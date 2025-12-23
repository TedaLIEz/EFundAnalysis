"""Factory pattern for creating LLM instances from different providers."""

from collections.abc import Callable
import os
from typing import Literal

from dotenv import load_dotenv
from llama_index.core.llms.function_calling import FunctionCallingLLM

from .aopenai import create_llm as create_azure_openai_llm
from .siliconflow import create_llm as create_siliconflow_llm

load_dotenv()

LLMProvider = Literal["azure_openai", "siliconflow"]


class LLMFactory:
    """Factory for creating LLM instances from different providers."""

    _providers: dict[str, Callable[[], FunctionCallingLLM]] = {
        "azure_openai": create_azure_openai_llm,
        "siliconflow": create_siliconflow_llm,
    }

    @classmethod
    def create(cls, provider: LLMProvider | None = None) -> FunctionCallingLLM:
        """Create an LLM instance from the specified provider.

        Args:
            provider: The provider name ("azure_openai" or "siliconflow").
                If None, uses the LLM_PROVIDER environment variable or defaults to "azure_openai".

        Returns:
            FunctionCallingLLM: Configured LLM instance.

        Raises:
            ValueError: If the specified provider is not supported.

        """
        if provider is None:
            provider_str = os.getenv("LLM_PROVIDER", "azure_openai")
            provider = provider_str if provider_str in cls._providers else "azure_openai"  # type: ignore[assignment]

        if provider not in cls._providers:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {supported}")

        return cls._providers[provider]()

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get a list of supported LLM providers.

        Returns:
            list[str]: List of supported provider names.

        """
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, factory_func: Callable[[], FunctionCallingLLM]) -> None:
        """Register a new LLM provider factory function.

        Args:
            name: The provider name.
            factory_func: A callable that returns a FunctionCallingLLM instance.

        """
        cls._providers[name] = factory_func
