"""Conversation state manager."""

import os
import json
import datetime

from loguru import logger

from ..models import Config

ROLE_MAP = {"llm1": "user", "llm2": "assistant"}


class StateManager:
    """Manages conversation state and output persistence."""

    def __init__(self, conf: Config):
        self.conf = conf
        self.system_prompts = self._load_system_prompts()
        self.initial_history = self._load_initial_history()
        self.output_data = self._initialize_output_data()
        self.output_file = self._create_output_path()

    def _load_system_prompts(self) -> dict[str, str]:
        prompts: dict[str, str] = {}
        for llm_key in ["llm1", "llm2"]:
            llm_config = getattr(self.conf, llm_key)
            try:
                with open(llm_config.system_prompt_file, "r", encoding="utf-8") as fp:
                    prompts[llm_key] = fp.read()
            except FileNotFoundError:
                logger.error(f"System prompt file not found: {llm_config.system_prompt_file}")
                raise
        return prompts

    def _load_initial_history(self) -> list[dict[str, str]]:
        if self.conf.history_file:
            try:
                with open(self.conf.history_file, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            except FileNotFoundError:
                logger.error(f"History file not found: {self.conf.history_file}")
                raise
        elif self.conf.history:
            return self.conf.history
        raise ValueError("Either 'history_file' or 'history' must be provided in the configuration.")

    def _initialize_output_data(self) -> dict:
        return {
            "participants": {
                "user": {
                    "model": self.conf.llm1.connection,
                    "system_prompt": self.system_prompts["llm1"],
                },
                "assistant": {
                    "model": self.conf.llm2.connection,
                    "system_prompt": self.system_prompts["llm2"],
                },
            },
            "config": {
                "rounds": self.conf.rounds,
                "initial_history": self.initial_history,
            },
            "messages": [],
        }

    def _create_output_path(self) -> str | None:
        if not self.conf.output_file:
            return None
        base, ext = os.path.splitext(self.conf.output_file)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{base}-{timestamp}{ext}"

    def append_message(self, llm_key: str, content: str) -> None:
        """Record a message with the correct role and persist to output file."""
        role = ROLE_MAP[llm_key]
        self.output_data["messages"].append({"role": role, "content": content})
        if self.output_file:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.output_data, f, indent=2)
