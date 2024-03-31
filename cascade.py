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

from halo import Halo
from loguru import logger
from datetime import datetime
from rich.console import Console
from typing import Any, Dict, List, Optional
from pydantic import ValidationError

from cascade.utils import create_panel, write_json
from cascade.models import Conversation, Message
from cascade.llm.anthropic import AnthropicWrapper
from cascade.llm.openai import OpenAIWrapper
from cascade.llm.ollama import OllamaWrapper


console = Console()


class ConversationManager:
    def __init__(self, 
        llm_1: str,
        llm_2: str,
        history: List[Dict[str, str]],
        sys_prompt1: str,
        sys_prompt2: str,
        rounds: int = 5,
        output_file: Optional[str] = None
    ) -> None:
        self.llm_1 = llm_1
        self.llm_2 = llm_2
        self.conv_1 = history
        self.conv_2 = Conversation(messages=[])
        self.rounds = rounds
        self.output_file = output_file
        self.sys_prompt1 = sys_prompt1
        self.sys_prompt2 = sys_prompt2
        self.clients: Dict[str, Any] = {llm_1: None, llm_2: None}

        for llm in [self.llm_1, self.llm_2]:
            if llm in ['anthropic', 'openai']:
                if llm == 'anthropic':
                    self.clients[llm] = AnthropicWrapper()
                elif llm == 'openai':
                    self.clients[llm] = OpenAIWrapper()
            else:
                try:
                    ollama_model = llm.split('ollama:')[1]
                    self.clients[llm] = OllamaWrapper(ollama_model)
                except IndexError:
                    logger.error(f"Invalid Ollama model name (use format `ollama:model`): {llm}")
                    sys.exit(1)

    def converse(self) -> None:
        self._converse()

        if self.output_file:
            write_json(
                {
                    "conversation_1": self.conv_1.model_dump(),
                    "conversation_2": self.conv_2.model_dump()
                }, 
                self.output_file
            )

    def _converse(self) -> None:
        for i in range(1, self.rounds + 1):
            sequence = [
                (self.conv_1, self.llm_1, self.sys_prompt1, self.conv_2),
                (self.conv_2, self.llm_2, self.sys_prompt2, self.conv_1)
            ]

            for conv, llm, sys_prompt, other_conv in sequence:
                response = self._generate_response(conv, llm, sys_prompt, round_num=i)
                new_message = Message(role="assistant", content=response)
                conv.messages.append(new_message)

                other_conv_new_message = Message(role="user", content=response)
                other_conv.messages.append(other_conv_new_message)
                time.sleep(2)

    def _generate_response(self, conversation: Conversation, bot_name: str, sys_prompt: str, round_num: int) -> str:
        spinner = Halo(text='Loading...', spinner='dots')
        spinner.text = f"(#r{round_num}) {bot_name} loading..."
        spinner.start()
        response = ""

        try:
            response = self.clients[bot_name].generate(conversation.messages, sys_prompt)
            spinner.stop()
            spinner.clear()

            panel = create_panel(
                    response,
                    title=f'{bot_name} (#r{round_num})',
                    timestamp=datetime.now(),
                    color="blue" if bot_name == "anthropic" else "green",
                )
            console.print(panel)

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            spinner.fail("Failed")
            console.print_exception()
            sys.exit(1)

        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--llm1",
        type=str,
        default='anthropic',
        help="First LLM (anthropic, openai, ollama:*)"
    )

    parser.add_argument(
        "--llm2",
        type=str,
        default='anthropic',
        help="Second LLM (anthropic, openai, ollama:*)"
    )

    parser.add_argument(
        "-s1",
        "--sys_prompt1",
        action="store",
        default="data/prompts/simulation.txt",
        help="Path to system prompt for LLM 1"
    )

    parser.add_argument(
        "-s2",
        "--sys_prompt2",
        action="store",
        default="data/prompts/pirate.txt",
        help="Path to system prompt for LLM2"
    )

    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=5,
        help="Number of exchanges between the instances"
    )

    parser.add_argument(
        "-c",
        "--chat",
        type=str,
        default="",
        help="Path to initial chat history"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        required=False,
        help="File to save conversation to" 
    )

    args = parser.parse_args()

    if not os.path.exists(args.sys_prompt1) or not os.path.exists(args.sys_prompt2):
        logger.error("System prompt file not found")
        sys.exit(1)

    with open(args.sys_prompt1, "r") as file:
        system_prompt1 = file.read()
    
    with open(args.sys_prompt2, "r") as file:
        system_prompt2 = file.read()

    if args.chat and os.path.exists(args.chat):
        try:
            with open(args.chat, "r") as fp:
                data = json.load(fp)
                chat_history = Conversation(messages=data)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading chat history: {e}")
            sys.exit(1)
        except ValidationError as e:
            logger.error(f"Invalid chat history structure: {e}")
            sys.exit(1)
    else:
        chat_history = Conversation(messages=[])

    logger.info(f"Starting conversation: {args.llm1} ⇄ {args.llm2}")

    manager = ConversationManager(
        llm_1=args.llm1,
        llm_2=args.llm2,
        history=chat_history,
        sys_prompt1=system_prompt1,
        sys_prompt2=system_prompt2,
        rounds=args.rounds,
        output_file=args.output,
    )

    try:
        manager.converse()
    except KeyboardInterrupt:
        logger.error("Conversation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
