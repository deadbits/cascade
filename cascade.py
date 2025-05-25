"""
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
~ cascade.py ~
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
"""

import os
import sys
import argparse
from typing import Dict

import yaml
from loguru import logger
from pydantic import ValidationError

from cascade.llm.base import BaseLLMWrapper
from cascade.llm.anthropic import AnthropicWrapper
from cascade.llm.openai import OpenAIWrapper
from cascade.llm.ollama import OllamaWrapper
from cascade.models import Config
from cascade.core.orchestrator import ConversationOrchestrator
from cascade.core.conversation import StateManager
from cascade.core.display import DisplayManager


def initialize_llm_wrappers(conf: Config) -> Dict[str, BaseLLMWrapper]:
    """Initialize LLM wrappers based on configuration."""
    wrappers = {}
    for llm_key in ["llm1", "llm2"]:
        llm_config = getattr(conf, llm_key)
        provider = llm_config.provider
        model = llm_config.model

        if provider == "anthropic":
            wrappers[llm_key] = AnthropicWrapper(model=model)
        elif provider == "openai":
            wrappers[llm_key] = OpenAIWrapper(model=model)
        elif provider == "ollama":
            wrappers[llm_key] = OllamaWrapper(model=model)
        else:
            raise ValueError(f"Invalid LLM provider: {provider}")

    return wrappers


def load_config(config_file: str) -> tuple[Config, str]:
    """Load the configuration file."""
    config_dir = os.path.dirname(os.path.abspath(config_file))
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    try:
        return Config(**config_data), config_dir
    except ValidationError as validation_err:
        logger.error(f"Invalid configuration: {validation_err}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to YAML configuration file",
    )
    args = parser.parse_args()

    config, config_dir = load_config(args.config)
    logger.info(
        f"Starting conversation: {config.llm1.connection} ⇄ {config.llm2.connection}"
    )

    llm_wrappers = initialize_llm_wrappers(config)
    state_manager = StateManager(config, config_dir)
    display_manager = DisplayManager()

    orchestrator = ConversationOrchestrator(
        conf=config,
        conf_dir=config_dir,
        llm_wrappers=llm_wrappers,
        state_manager=state_manager,
        display_manager=display_manager,
    )

    try:
        orchestrator.converse()
    except KeyboardInterrupt:
        logger.error("Conversation interrupted by user")
        sys.exit(1)
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        sys.exit(1)
