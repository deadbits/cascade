"""Wrapper for the Anthropic API."""
from typing import Generator
import os
import anthropic
from loguru import logger

from cascade.utils import escape_chars


class AnthropicWrapper:
    """Wrapper for the Anthropic API."""
    def __init__(self):
        self.name = "anthropic"
        if os.environ.get('ANTHROPIC_API_KEY'):
            self.client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        else:
            raise ValueError("Anthropic API key not found")

    def generate(self, conversation, system_prompt=None):
        """Generate a response."""
        formatted = ""

        try:
            params = {
                'model': 'claude-3-opus-20240229',
                'max_tokens': 1024,
                'messages': conversation,
            }
            if system_prompt:
                params['system'] = system_prompt

            response = self.client.messages.create(**params)
            formatted = escape_chars(response.content[0].text)
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            logger.error(f"Anthropic API error: {e}")
            return str(e)

        return formatted

    def generate_stream(self, messages, system_prompt=None) -> Generator[str, None, None]:
        """Generate a streaming response."""
        try:
            params = {
                'model': 'claude-3-opus-20240229',
                'max_tokens': 1024,
                'messages': messages,
            }
            if system_prompt:
                params['system'] = system_prompt

            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield escape_chars(text)
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            logger.error(f"Anthropic API error: {e}")
            yield f"Error: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in generate_stream")
            yield f"An unexpected error occurred: {str(e)}"
