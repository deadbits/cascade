"""Wrapper for the Ollama API."""
import ollama

from cascade.utils import escape_chars


class OllamaWrapper:
    """Wrapper for the Ollama API."""
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def generate(self, conversation, system_prompt=None):
        """Generate a response."""
        formatted = ""

        if system_prompt:
            conversation.insert(0, {"role": "system", "content": system_prompt})

        try:
            response = ollama.chat(
                self.model_name,
                messages=conversation
            )
            formatted = escape_chars(response['message']['content'])
        except Exception as e:
            return str(e)

        return formatted
