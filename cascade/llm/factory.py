"""Create LLM wrappers."""

from typing import Dict, Type
import os
from cascade.models import Provider
from cascade.llm.base import BaseLLMWrapper
from cascade.llm.anthropic import AnthropicWrapper
from cascade.llm.openai import OpenAIWrapper
from cascade.llm.ollama import OllamaWrapper


class LLMFactory:
    """Factory for creating LLM wrappers."""

    _registry: Dict[Provider, Type[BaseLLMWrapper]] = {
        Provider.ANTHROPIC: AnthropicWrapper,
        Provider.OPENAI: OpenAIWrapper,
        Provider.OLLAMA: OllamaWrapper,
    }

    @classmethod
    def create(cls, config) -> BaseLLMWrapper:
        """Create an LLM wrapper instance from an LLMConfig."""
        provider = config.provider
        if provider not in cls._registry:
            raise ValueError(f"Unknown provider: {provider}")

        wrapper_class = cls._registry[provider]
        if provider in [Provider.OPENAI, Provider.ANTHROPIC]:
            config.require_api_key()
            api_key = os.environ[provider.upper() + "_API_KEY"]
            return wrapper_class(model=config.model, api_key=api_key)
        else:
            return wrapper_class(model=config.model)

    @classmethod
    def register(cls, provider: Provider, wrapper_class: Type[BaseLLMWrapper]) -> None:
        """Register a new LLM wrapper."""
        cls._registry[provider] = wrapper_class
