"""Conversation manager."""

from dataclasses import dataclass
import os
import json
from loguru import logger
import datetime

from cascade.models import (
    Conversation,
    Message,
    Config,
)


@dataclass
class ConversationPair:
    """A pair of conversations between two LLMs."""

    llm1: str
    llm2: str
    conversation1: Conversation
    conversation2: Conversation

    def get_llm_conversation(self, llm_key: str) -> Conversation:
        """Get the conversation for a specific LLM."""
        return self.conversation1 if llm_key == self.llm1 else self.conversation2

    def get_other_llm_key(self, llm_key: str) -> str:
        """Get the key of the other LLM."""
        return self.llm2 if llm_key == self.llm1 else self.llm1

    def add_message(self, llm_key: str, message: Message) -> None:
        """Add a message to the conversation and mirror it to the other side."""
        self.get_llm_conversation(llm_key).messages.append(message)

        # Mirror to the other conversation with opposite role
        other_llm_key = self.get_other_llm_key(llm_key)
        other_message = Message(
            role="user" if message.role == "assistant" else "assistant",
            content=message.content,
        )
        self.get_llm_conversation(other_llm_key).messages.append(other_message)


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
            llm1="llm1",
            llm2="llm2",
            conversation1=conv_1,
            conversation2=Conversation(messages=[]),
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
