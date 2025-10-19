"""
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
~ cascade.py ~
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
"""

import os
import sys
import argparse

import yaml
from loguru import logger
from pydantic import ValidationError

from cascade.llm.factory import LLMFactory
from cascade.models import Config
from cascade.core.orchestrator import ConversationOrchestrator
from cascade.core.conversation import StateManager
from cascade.core.display import DisplayManager


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

    llm_wrappers = {
        "llm1": LLMFactory.create(config.llm1),
        "llm2": LLMFactory.create(config.llm2)
    }

    state_manager = StateManager(config)
    display_manager = DisplayManager()

    orchestrator = ConversationOrchestrator(
        conf=config,
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
