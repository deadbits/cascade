"""
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
~ cascade.py ~
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
"""

import os
import json
import sys
import argparse
import asyncio
from typing import Dict
from datetime import datetime
from pathlib import Path

import yaml
from loguru import logger
from rich.console import Console, Group
from rich.live import Live
from rich import box
from rich.panel import Panel
from rich.markdown import Markdown
from pydantic import ValidationError

from cascade.llm.agent import AgentWrapper
from cascade.models import Conversation, Message, Config


console = Console()


class ConversationManager:
    """Manage a conversation between two language models."""

    def __init__(self, conf: Config, conf_dir: str):
        self.conf = conf
        self.conf_dir = conf_dir
        self.sys_prompts = self._load_system_prompts()
        self.llm_wrappers = self._initialize_llm_wrappers()
        self.conversations = self._initialize_conversations()
        self.output_data = {"conversation_1": [], "conversation_2": []}
        self.output_file = self._initialize_output_file()

    def _initialize_llm_wrappers(self) -> Dict[str, AgentWrapper]:
        return {
            "llm1": AgentWrapper(self.conf.llm1.connection, self.sys_prompts["llm1"]),
            "llm2": AgentWrapper(self.conf.llm2.connection, self.sys_prompts["llm2"]),
        }

    def _initialize_conversations(self) -> Dict[str, Conversation]:
        conv_1 = self._load_conversation_history()
        return {"conv_1": conv_1, "conv_2": Conversation(messages=[])}

    def _load_conversation_history(self) -> Conversation:
        if self.conf.history_file:
            try:
                with open(
                    os.path.join(self.conf_dir, self.conf.history_file),
                    "r",
                    encoding="utf-8",
                ) as fp:
                    return Conversation(messages=json.load(fp))
            except Exception as err:
                logger.error(f"{err}: {self.conf.history_file}")
                sys.exit(1)

        elif self.conf.history:
            return Conversation(messages=self.conf.history)
        else:
            raise ValueError(
                "Either 'history_file' or 'history' must be provided in the configuration."
            )

    def _load_system_prompts(self) -> Dict[str, str]:
        prompts = {}
        for llm in ["llm1", "llm2"]:
            file_path = os.path.join(
                self.conf_dir, getattr(self.conf, llm).system_prompt_file
            )
            try:
                with open(file_path, "r", encoding="utf-8") as fp:
                    prompts[llm] = fp.read()
            except FileNotFoundError:
                logger.error(f"System prompt file not found: {file_path}")
                sys.exit(1)
        return prompts

    def _initialize_output_file(self) -> str:
        """Initialize output file with unique timestamp-based name."""
        if self.conf.output_file:
            output_path = Path(os.path.join(self.conf_dir, self.conf.output_file))
            output_dir = output_path.parent
            base_name = output_path.stem
            extension = output_path.suffix

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{base_name}_{timestamp}{extension}"

            output_dir.mkdir(parents=True, exist_ok=True)

            return str(output_dir / new_filename)
        return None

    def _append_and_write_message(self, conv_key: str, message: Message) -> None:
        self.output_data[conv_key].append(message.model_dump())
        if self.output_file:
            try:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    json.dump(self.output_data, f, indent=2)
            except IOError as e:
                logger.error(f"Failed to write to output file: {e}")
                # Continue execution but log the error

    async def _generate_response(
        self, llm_key: str, conversation: Conversation, round_num: int
    ) -> str:
        response = ""
        color = "blue" if llm_key == "llm1" else "green"
        markdown_content = ""

        def update_panel():
            md = Markdown(markdown_content)
            panel.renderable = Group(md)
            live.update(panel)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            Group(),
            title=f"{getattr(self.conf, llm_key).connection} (#r{round_num}) - {timestamp}",
            border_style=color,
            box=box.DOUBLE_EDGE,
            expand=False,
        )

        with Live(panel, refresh_per_second=4) as live:
            try:
                prev = ""
                async for chunk in self.llm_wrappers[llm_key].generate_stream(
                    conversation.messages
                ):
                    # Only append the new part of the chunk
                    new_text = chunk[len(prev) :] if chunk.startswith(prev) else chunk
                    response += new_text
                    markdown_content += new_text
                    prev = chunk
                    update_panel()
            except Exception as ex:
                logger.error(f"Error generating response: {str(ex)}")
                sys.exit(1)

        return response

    def _process_human_input(self, conv: Conversation, llm_key: str):
        if self.conf.human_in_the_loop:
            try:
                human_message = input(
                    f"msg ({getattr(self.conf, llm_key).type}): "
                ).strip()
                conv.messages[-1].content += f"\n\n<HUMAN>{human_message}</HUMAN>\n"
                self._append_and_write_message(
                    f"conversation_{llm_key[-1]}", conv.messages[-1]
                )
            except KeyboardInterrupt:
                logger.debug("User skipped message")

    async def converse(self):
        """Start conversation."""
        for i in range(1, self.conf.rounds + 1):
            for llm_key, conv_key, other_conv_key in [
                ("llm1", "conv_1", "conv_2"),
                ("llm2", "conv_2", "conv_1"),
            ]:
                self._process_human_input(self.conversations[conv_key], llm_key)

                response = await self._generate_response(
                    llm_key, self.conversations[conv_key], i
                )
                new_message = Message(role="assistant", content=response)
                self.conversations[conv_key].messages.append(new_message)
                self._append_and_write_message(
                    f"conversation_{llm_key[-1]}", new_message
                )

                other_conv_new_message = Message(role="user", content=response)
                self.conversations[other_conv_key].messages.append(
                    other_conv_new_message
                )
                self._append_and_write_message(
                    f"conversation_{3 - int(llm_key[-1])}", other_conv_new_message
                )

                await asyncio.sleep(2)


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

    manager = ConversationManager(config, config_dir)

    try:
        asyncio.run(manager.converse())
    except KeyboardInterrupt:
        logger.error("Conversation interrupted by user")
        sys.exit(1)
    except Exception as err:
        logger.error(f"An error occurred: {err}")
        sys.exit(1)
