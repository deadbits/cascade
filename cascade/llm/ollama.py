"""Wrapper for the Ollama API."""

from typing import Generator
import ollama
from loguru import logger

from cascade.utils import escape_chars
from cascade.llm.base import BaseLLMWrapper


class OllamaWrapper(BaseLLMWrapper):
    """Wrapper for the Ollama API."""

    def __init__(self, model: str):
        """Initialize the Ollama wrapper.

        Args:
            model: The model identifier to use
        """
        super().__init__(model)

    def generate_stream(
        self, messages, system_prompt=None
    ) -> Generator[str, None, None]:
        """Generate a streaming response."""
        messages = [msg.model_dump() for msg in messages]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            for part in ollama.chat(self.model, messages=messages, stream=True):
                yield escape_chars(part["message"]["content"])
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            yield f"Error: {str(e)}"
