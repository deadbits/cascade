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
    """Conversation pair management."""

    conversations: Dict[str, Conversation] = field(default_factory=dict)

    def __post_init__(self):
        if not self.conversations:
            self.conversations = {
                "llm1": Conversation(messages=[]),
                "llm2": Conversation(messages=[]),
            }

    def add_message(self, sender: str, message: Message) -> None:
        """Add a message and mirror it to the other conversation."""
        self.conversations[sender].messages.append(message)

        receiver = "llm2" if sender == "llm1" else "llm1"
        mirrored_message = Message(
            role="user" if message.role == "assistant" else "assistant",
            content=message.content,
        )
        self.conversations[receiver].messages.append(mirrored_message)

    def get_conversation(self, llm_key: str) -> Conversation:
        """Get conversation for a specific LLM."""
        return self.conversations[llm_key]


class StateManager:
    """Manages conversation state."""

    def __init__(self, conf: Config):
        self.conf = conf
        self.conversation_pair = self._initialize_conversations()
        self.output_data = self._initialize_output_data()
        self.output_file = None
        if self.conf.output_file:
            base, ext = os.path.splitext(self.conf.output_file)
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self.output_file = f"{base}-{timestamp}{ext}"

    def _initialize_output_data(self) -> Dict:
        """Initialize output data with the new format."""
        return {
            "llm1": {
                "model": self.conf.llm1.connection,
                "system_prompt": self._load_system_prompt("llm1"),
                "chat_history": [],
            },
            "llm2": {
                "model": self.conf.llm2.connection,
                "system_prompt": self._load_system_prompt("llm2"),
                "chat_history": [],
            },
            "rounds": self.conf.rounds,
            "messages": [],
        }

    def _load_system_prompt(self, llm_key: str) -> str:
        """Load system prompt content from file."""
        llm_config = getattr(self.conf, llm_key)
        try:
            with open(llm_config.system_prompt_file, "r", encoding="utf-8") as fp:
                return fp.read()
        except FileNotFoundError:
            logger.error(
                f"System prompt file not found: {llm_config.system_prompt_file}"
            )
            return ""

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
                    os.path.join(self.conf.history_file),
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

        # Add to global messages list only (chat_history is the initial history)
        msg_dict = {"role": message.role, "content": message.content}
        self.output_data["messages"].append(msg_dict)

        if self.output_file:
            with open(
                os.path.join(self.output_file),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(self.output_data, f, indent=2)
