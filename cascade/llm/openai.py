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


class OpenAIWrapper:
    """Wrapper for OpenAI API"""
    def __init__(self):
        self.name = "openai"
        if os.environ.get('OPENAI_API_KEY'):
            self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        else:
            raise ValueError("OpenAI API key not found in environment variables")

    def generate(self, conversation, system_prompt=None):
        """Generate a response."""
        formatted = ""

        if system_prompt:
            conversation.insert(0, {"role": "system", "content": system_prompt})

        try:
            response = self.client.chat.completions.create(
                model='gpt-4-1106-preview',
                messages=conversation,
            )
            formatted = escape_chars(response.choices[0].message.content)
        except (APIError, APIConnectionError, RateLimitError) as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "An unexpected error occurred"

        return formatted

    def generate_stream(self, messages, system_prompt=None) -> Generator[str, None, None]:
        """Generate a streaming response."""
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            stream = self.client.chat.completions.create(
                model='gpt-4-1106-preview',
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield escape_chars(chunk.choices[0].delta.content)
        except Exception as e:
            yield str(e)
