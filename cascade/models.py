"""Models for Cascade."""
from typing import List, Dict, Optional
from pydantic import BaseModel, model_validator


class Message(BaseModel):
    """Message."""
    role: str
    content: str

class Conversation(BaseModel):
    """Conversation."""
    messages: List[Message]

class LLMConfig(BaseModel):
    """LLM config."""
    type: str
    system_prompt_file: str

class Config(BaseModel):
    """YAML Config."""
    llm1: LLMConfig
    llm2: LLMConfig
    rounds: int
    output_file: str
    history: Optional[List[Dict[str, str]]] = None
    history_file: Optional[str] = None

    @model_validator(mode='after')
    def check_history(cls, values):
        """Check that either 'history' or 'history_file' is provided."""
        if values.history is None and values.history_file is None:
            raise ValueError("Either 'history' or 'history_file' must be provided")
        return values
