"""Wrapper for OpenAI API"""

from typing import Generator
import os

from openai import (
    OpenAI,
    APIError,
    APIConnectionError,
    RateLimitError,
)
from loguru import logger

from cascade.utils import escape_chars
from cascade.llm.base import BaseLLMWrapper


class OpenAIWrapper(BaseLLMWrapper):
    """Wrapper for OpenAI API"""

    def __init__(self, model: str, api_key: str):
        """Initialize the OpenAI wrapper.

        Args:
            model: The model identifier to use
            api_key: The OpenAI API key
        """
        super().__init__(model)
        self.client = OpenAI(api_key=api_key)

    def generate_stream(
        self, messages, system_prompt=None
    ) -> Generator[str, None, None]:
        """Generate a streaming response."""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield escape_chars(chunk.choices[0].delta.content)
        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"OpenAI API error: {e}")
            yield f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            yield "An unexpected error occurred"
