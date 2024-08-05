"""
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
~ cascade.py ~
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.

start a conversation between two LLM instances

set api keys with `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`
"""
import os
import json
import sys
import time
import argparse
import yaml

from halo import Halo
from loguru import logger
from datetime import datetime
from rich.console import Console
from typing import Any, Dict
from pydantic import ValidationError

from cascade.utils import create_panel, write_json
from cascade.models import Conversation, Message, Config
from cascade.llm.anthropic import AnthropicWrapper
from cascade.llm.openai import OpenAIWrapper
from cascade.llm.ollama import OllamaWrapper

console = Console()



class ConversationManager:
    """Manage a conversation between two language models."""
    def __init__(self, conf: Config, conf_dir: str) -> None:
        self.llm_1 = conf.llm1.type
        self.llm_2 = conf.llm2.type
        self.rounds = conf.rounds
        self.output_file = os.path.join(conf_dir, conf.output_file) if conf.output_file else None
        self.hitl = conf.human_in_the_loop
        self.output_data = {"conversation_1": [], "conversation_2": []}

        if self.hitl:
            logger.warning(
                "Human-in-the-loop mode enabled. Press Ctrl+C on your input to skip a round."
            )

        try:
            with open(
                os.path.join(conf_dir, conf.llm1.system_prompt_file), 'r', encoding='utf-8'
            ) as fp:
                self.sys_prompt1 = fp.read()
        except FileNotFoundError:
            logger.error(f"System prompt file not found: {conf.llm1.system_prompt_file}")
            sys.exit(1)

        try:
            with open(
                os.path.join(conf_dir, conf.llm2.system_prompt_file), 'r', encoding='utf-8'
            ) as fp:
                self.sys_prompt2 = fp.read()
        except FileNotFoundError:
            logger.error(f"System prompt file not found: {conf.llm2.system_prompt_file}")
            sys.exit(1)

        if conf.history_file:
            try:
                with open(os.path.join(conf_dir, conf.history_file), 'r', encoding='utf-8') as fp:
                    self.conv_1 = Conversation(messages=json.load(fp))
            except FileNotFoundError:
                logger.error(f"History file not found: {conf.history_file}")
                sys.exit(1)
        elif conf.history:
            self.conv_1 = Conversation(messages=conf.history)
        else:
            raise ValueError(
                "Either 'history_file' or 'history' must be provided in the configuration."
            )

        self.conv_2 = Conversation(messages=[])
        self.clients: Dict[str, Any] = {self.llm_1: None, self.llm_2: None}

        for llm in [self.llm_1, self.llm_2]:
            if llm in ["anthropic", "openai"]:
                if llm == "anthropic":
                    self.clients[llm] = AnthropicWrapper()
                elif llm == "openai":
                    self.clients[llm] = OpenAIWrapper()
            else:
                try:
                    ollama_model = llm.split("ollama:")[1]
                    self.clients[llm] = OllamaWrapper(ollama_model)
                except IndexError:
                    logger.error(f"Invalid Ollama model name (use format `ollama:model`): {llm}")
                    sys.exit(1)

    def _append_and_write_message(self, conv_key: str, message: Message) -> None:
        """Append a message to the output data and write it to the file."""
        self.output_data[conv_key].append(message.model_dump())
        if self.output_file:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.output_data, f, indent=2)

    def converse(self) -> None:
        """Start the conversation between the two instances."""
        self._converse()

    def _converse(self) -> None:
        for i in range(1, self.rounds + 1):
            sequence = [
                (self.conv_1, self.llm_1, self.sys_prompt1, self.conv_2, "conversation_1"),
                (self.conv_2, self.llm_2, self.sys_prompt2, self.conv_1, "conversation_2"),
            ]

            for conv, llm, sys_prompt, other_conv, conv_key in sequence:
                if self.hitl:
                    try:
                        human_message = input(f"msg ({llm}): ").strip()
                        conv.messages[-1].content += f"\n\n<HUMAN>{human_message}</HUMAN>\n"
                        self._append_and_write_message(conv_key, conv.messages[-1])
                    except KeyboardInterrupt:
                        logger.debug("User skipped message")

                response = self._generate_response(conv, llm, sys_prompt, round_num=i)
                new_message = Message(role="assistant", content=response)
                conv.messages.append(new_message)
                self._append_and_write_message(conv_key, new_message)

                other_conv_new_message = Message(role="user", content=response)
                other_conv.messages.append(other_conv_new_message)
                self._append_and_write_message(
                    "conversation_2" if conv_key == "conversation_1" else "conversation_1",
                    other_conv_new_message
                )

                time.sleep(2)

    def _generate_response(
        self, conversation: Conversation,
        bot_name: str,
        sys_prompt: str,
        round_num: int
    ) -> str:
        spinner = Halo(text="Loading...", spinner="dots")
        spinner.text = f"(#r{round_num}) {bot_name} loading..."
        spinner.start()
        response = ""

        try:
            response = self.clients[bot_name].generate(
                conversation.messages, sys_prompt
            )
            spinner.stop()
            spinner.clear()

            panel = create_panel(
                response,
                title=f"{bot_name} (#r{round_num})",
                timestamp=datetime.now(),
                color="blue" if bot_name == "anthropic" else "green",
            )
            console.print(panel)

        except Exception as ex:
            logger.error(f"Error generating response: {str(ex)}")
            spinner.fail("Failed")
            console.print_exception()
            sys.exit(1)

        return response


def load_config(config_file: str) -> tuple[Config, str]:
    """Load the configuration from a YAML file and return the config directory."""
    config_dir = os.path.dirname(os.path.abspath(config_file))

    with open(config_file, 'r', encoding='utf-8') as f:
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
        help="Path to YAML configuration file"
    )
    args = parser.parse_args()

    config, config_dir = load_config(args.config)

    logger.info(f"Starting conversation: {config.llm1.type} ⇄ {config.llm2.type}")

    manager = ConversationManager(config, config_dir)

    try:
        manager.converse()
    except KeyboardInterrupt:
        logger.error("Conversation interrupted by user")
        sys.exit(1)
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit(1)
