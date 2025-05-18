from pydantic_ai import Agent
from cascade.llm.ollama import OllamaWrapper


class AgentWrapper:
    def __init__(self, connection: str, system_prompt: str):
        if connection.startswith("ollama:"):
            self.provider = "ollama"
            self.model = connection.split(":", 1)[1]
            self.agent = OllamaWrapper(self.model)
            self.system_prompt = system_prompt
        else:
            self.provider = "pydantic"
            self.agent = Agent(connection, system_prompt=system_prompt)

    async def generate_stream(self, messages, message_history=None):
        if self.provider == "ollama":
            # OllamaWrapper expects a list of dicts, and is sync
            for chunk in self.agent.generate_stream(messages, self.system_prompt):
                yield chunk
        else:
            prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
            async with self.agent.run_stream(
                prompt, message_history=message_history
            ) as result:
                async for chunk in result.stream_text():
                    yield chunk
