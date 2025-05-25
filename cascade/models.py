"""Models for Cascade."""

from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, model_validator, field_validator
import os


class Provider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


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
        try:
            Provider(provider)
        except ValueError:
            raise ValueError(f"Provider must be one of: {[p.value for p in Provider]}")
        return v

    @property
    def provider(self) -> str:
        """Get the provider from the connection string."""
        return self.connection.split(":", 1)[0]

    @property
    def model(self) -> str:
        """Get the model from the connection string."""
        return self.connection.split(":", 1)[1]

    def require_api_key(self):
        """Ensure the required API key is present in the environment for providers that need it."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        env_var = env_vars.get(self.provider)
        if env_var and not os.environ.get(env_var):
            raise ValueError(f"{env_var} must be set in the environment for provider '{self.provider}'")


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
