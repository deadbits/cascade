"""Wrapper for the Anthropic API."""

from typing import Generator
import os
import anthropic
from loguru import logger

from cascade.utils import escape_chars
from cascade.llm.base import BaseLLMWrapper


class AnthropicWrapper(BaseLLMWrapper):
    """Wrapper for the Anthropic API."""

    def __init__(self, model: str, api_key: str):
        """Initialize the Anthropic wrapper.

        Args:
            model: The model identifier to use
            api_key: The Anthropic API key
        """
        super().__init__(model)
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_stream(
        self, messages, system_prompt=None
    ) -> Generator[str, None, None]:
        """Generate a streaming response."""
        try:
            params = {
                "model": self.model,
                "max_tokens": 1024,
                "messages": messages,
            }
            if system_prompt:
                params["system"] = system_prompt

            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield escape_chars(text)
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            logger.error(f"Anthropic API error: {e}")
            yield f"Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in generate_stream")
            yield f"An unexpected error occurred: {str(e)}"
