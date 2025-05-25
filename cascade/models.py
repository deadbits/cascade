"""Models for Cascade."""

from typing import List, Dict, Optional
from pydantic import BaseModel, model_validator, field_validator


class Message(BaseModel):
    """Message."""

    role: str
    content: str


class Conversation(BaseModel):
    """Conversation."""

    messages: List[Message]


class LLMConfig(BaseModel):
    """LLM config."""

    connection: str
    system_prompt_file: str

    @field_validator("connection")
    @classmethod
    def validate_connection(cls, v: str) -> str:
        """Validate the connection string format."""
        if ":" not in v:
            raise ValueError("Connection string must be in format 'provider:model'")
        provider, model = v.split(":", 1)
        if not provider or not model:
            raise ValueError("Both provider and model must be specified")
        if provider not in ["anthropic", "openai", "ollama"]:
            raise ValueError("Provider must be one of: anthropic, openai, ollama")
        return v

    @property
    def provider(self) -> str:
        """Get the provider from the connection string."""
        return self.connection.split(":", 1)[0]

    @property
    def model(self) -> str:
        """Get the model from the connection string."""
        return self.connection.split(":", 1)[1]


class Config(BaseModel):
    """YAML Config."""

    llm1: LLMConfig
    llm2: LLMConfig
    rounds: int
    output_file: str
    history: Optional[List[Dict[str, str]]] = None
    history_file: Optional[str] = None
    human_in_the_loop: Optional[bool] = False

    @model_validator(mode="after")
    def check_history(cls, values):
        """Check that either 'history' or 'history_file' is provided."""
        if values.history is None and values.history_file is None:
            raise ValueError("Either 'history' or 'history_file' must be provided")
        return values
