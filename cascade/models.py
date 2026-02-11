"""Models for Cascade."""

import os
import sys
from typing import Optional

from pydantic import BaseModel, model_validator, field_validator

_KEYLESS_PROVIDERS = {"ollama", "test"}


class LLMConfig(BaseModel):
    """LLM config."""

    connection: str
    system_prompt_file: str

    @field_validator("connection")
    @classmethod
    def validate_connection(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("Connection string must be in format 'provider:model'")
        provider, model = v.split(":", 1)
        if not provider or not model:
            raise ValueError("Both provider and model must be specified")
        return v

    @property
    def provider(self) -> str:
        return self.connection.split(":", 1)[0]

    @property
    def model(self) -> str:
        return self.connection.split(":", 1)[1]

    def require_api_key(self) -> None:
        """Exit with a clear error if the expected API key env var is missing."""
        if self.provider in _KEYLESS_PROVIDERS:
            return
        env_var = f"{self.provider.upper()}_API_KEY"
        if not os.environ.get(env_var):
            print(
                f"Error: {env_var} environment variable is required for "
                f"provider '{self.provider}' (connection: {self.connection})",
                file=sys.stderr,
            )
            sys.exit(1)


class Config(BaseModel):
    """YAML Config."""

    llm1: LLMConfig
    llm2: LLMConfig
    rounds: int
    output_file: str
    history: Optional[list[dict[str, str]]] = None
    history_file: Optional[str] = None
    human_in_the_loop: Optional[bool] = False

    @model_validator(mode="after")
    def check_history(cls, values):
        if values.history is None and values.history_file is None:
            raise ValueError("Either 'history' or 'history_file' must be provided")
        return values
