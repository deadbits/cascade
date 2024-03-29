import os

from openai import OpenAI

from cascade.utils import escape_chars


class OpenAIWrapper:
    def __init__(self):
        self.client = self.initialize_client()

    def initialize_client(self) -> OpenAI:
        if os.environ.get('OPENAI_API_KEY'):
            return OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        raise Exception("OpenAI API key not found")

    def generate(self, conversation, system_prompt=None):
        formatted = ""

        if system_prompt:
            conversation.insert(0, {"role": "system", "content": system_prompt})

        try:
            response = self.client.chat.completions.create(
                model='gpt-4-1106-preview',
                messages=conversation,
            )
            formatted = escape_chars(response.choices[0].message.content)
        except Exception as e:
            return str(e)

        return formatted