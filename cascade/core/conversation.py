"""Conversation manager."""

from dataclasses import dataclass, field
from typing import Dict
import os
import json
import datetime
from loguru import logger

from cascade.models import (
    Conversation,
    Message,
    Config,
)


@dataclass
class ConversationPair:
    """Simplified conversation pair management."""
    
    conversations: Dict[str, Conversation] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.conversations:
            self.conversations = {
                "llm1": Conversation(messages=[]),
                "llm2": Conversation(messages=[])
            }

    def add_message(self, sender: str, message: Message) -> None:
        """Add a message and mirror it to the other conversation."""
        self.conversations[sender].messages.append(message)
        
        receiver = "llm2" if sender == "llm1" else "llm1"
        mirrored_message = Message(
            role="user" if message.role == "assistant" else "assistant",
            content=message.content
        )
        self.conversations[receiver].messages.append(mirrored_message)
    
    def get_conversation(self, llm_key: str) -> Conversation:
        """Get conversation for a specific LLM."""
        return self.conversations[llm_key]

class StateManager:
    """Manages conversation state."""

    def __init__(self, conf: Config, conf_dir: str):
        self.conf = conf
        self.conf_dir = conf_dir
        self.conversation_pair = self._initialize_conversations()
        self.output_data = {
            "llm1": [],
            "llm2": [],
        }

    def _initialize_conversations(self) -> ConversationPair:
        """Initialize conversation history."""
        conv_1 = self._load_conversation_history()
        return ConversationPair(
            conversations={
                "llm1": conv_1,
                "llm2": Conversation(messages=[]),
            }
        )

    def _load_conversation_history(self) -> Conversation:
        """Load conversation history."""
        if self.conf.history_file:
            try:
                with open(
                    os.path.join(self.conf_dir, self.conf.history_file),
                    "r",
                    encoding="utf-8",
                ) as fp:
                    return Conversation(messages=json.load(fp))
            except FileNotFoundError:
                logger.error(f"History file not found: {self.conf.history_file}")
                raise
        elif self.conf.history:
            return Conversation(messages=self.conf.history)
        else:
            raise ValueError(
                "Either 'history_file' or 'history' must be provided in the configuration."
            )

    def append_message(self, llm_key: str, message: Message) -> None:
        """Append a message to the conversation."""
        self.conversation_pair.add_message(llm_key, message)
        msg_dict = message.model_dump()
        msg_dict["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        self.output_data[llm_key].append(msg_dict)

        if self.conf.output_file:
            with open(
                os.path.join(self.conf_dir, self.conf.output_file),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(self.output_data, f, indent=2)
