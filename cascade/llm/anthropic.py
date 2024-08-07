"""Wrapper for the Anthropic API."""
import os
import anthropic

from cascade.utils import escape_chars


class AnthropicWrapper:
    """Wrapper for the Anthropic API."""
    def __init__(self):
        self.client = self.initialize_client()

    def initialize_client(self) -> anthropic.Anthropic:
        """Initialize the Anthropic client."""
        if os.environ.get('ANTHROPIC_API_KEY'):
            return anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
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
        except Exception as e:
            return str(e)

        return formatted
