"""Config loader."""
import json
import os
import sys

import yaml
from pydantic import ValidationError

from loguru import logger

from .models import Config, Message


class ConfigLoader:
    """Load the configuration from a YAML file."""

    def __init__(self, config_file: str):
        """Load the configuration from a YAML file and return the config directory."""
        self.config_dir = os.path.dirname(os.path.abspath(config_file))
        self.system_prompts = {}
        self.messages = []

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        try:
            self.conf = Config(**data)
        except ValidationError as validation_err:
            logger.error(f"Invalid configuration: {validation_err}")
            raise validation_err

        self.load_system_prompts()
        self.load_messages()

    def load_system_prompts(self):
        """Load the system prompts from the configuration."""
        for llm in ["llm1", "llm2"]:
            prompt_file = getattr(self.conf, llm).system_prompt_file
            file_path = os.path.join(self.config_dir, prompt_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.system_prompts[llm] = f.read()
            except FileNotFoundError as exc:
                logger.error(f"System prompt file not found: {prompt_file}")
                raise FileNotFoundError(f"System prompt file not found: {prompt_file}") from exc

    def load_messages(self):
        """Load the messages from the configuration as a single list."""
        if self.conf.history_file:
            history_file_path = os.path.join(self.config_dir, self.conf.history_file)
            try:
                with open(history_file_path, "r", encoding="utf-8") as f:
                    history_data = json.load(f)
                    self.messages = [Message(**msg) for msg in history_data]
            except FileNotFoundError:
                logger.error(f"History file not found: {history_file_path}")
                sys.exit(1)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in history file: {history_file_path}")
                sys.exit(1)
        elif self.conf.history:
            self.messages = [Message(**msg) for msg in self.conf.history]
