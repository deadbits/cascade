"""
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
~ cascade cli ~
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
"""

import asyncio
import sys
import argparse

import yaml
from loguru import logger
from pydantic import ValidationError

from .agent import create_agent
from .models import Config
from .core.orchestrator import ConversationOrchestrator
from .core.conversation import StateManager
from .core.display import DisplayManager


def load_config(config_file: str) -> Config:
    """Load and validate the YAML configuration file."""
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    try:
        return Config(**config_data)
    except ValidationError as validation_err:
        logger.error(f"Invalid configuration: {validation_err}")
        sys.exit(1)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to YAML configuration file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    config.llm1.require_api_key()
    config.llm2.require_api_key()

    state_manager = StateManager(config)
    display_manager = DisplayManager()

    agents = {
        "llm1": create_agent(
            config.llm1.connection, state_manager.system_prompts["llm1"]
        ),
        "llm2": create_agent(
            config.llm2.connection, state_manager.system_prompts["llm2"]
        ),
    }

    orchestrator = ConversationOrchestrator(
        conf=config,
        agents=agents,
        state_manager=state_manager,
        display_manager=display_manager,
    )

    try:
        await orchestrator.converse()
    except KeyboardInterrupt:
        logger.error("Conversation interrupted by user")
        sys.exit(1)
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        sys.exit(1)


def entrypoint() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    entrypoint()
