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
from cascade.llm.anthropic import AnthropicWrapper
from cascade.llm.openai import OpenAIWrapper
from cascade.llm.ollama import OllamaWrapper


console = Console()


class ConversationManager:
    def __init__(self, 
        llm_1: str,
        llm_2: str,
        history: List[Dict[str, str]],
        system_prompt: str, 
        rounds: int = 5,
        output_file: Optional[str] = None
    ) -> None:
        self.llm_1 = llm_1
        self.llm_2 = llm_2
        self.conv_1 = history
        self.conv_2 = []
        self.rounds = rounds
        self.output_file = output_file
        self.system_prompt = system_prompt
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
                    "conversation_1": self.conv_1,
                    "conversation_2": self.conv_2
                }, 
                self.output_file
            )

    def _converse(self) -> None:
        for i in range(1, self.rounds + 1):
            sequence = [
                (self.conv_1, self.llm_1, self.conv_2),
                (self.conv_2, self.llm_2, self.conv_1)
            ]

            for conv, llm, other_conv in sequence:
                response = self._generate_response(conv, llm, system=True, round_num=i)
                conv.append(
                    {
                        "role": "assistant", 
                        "content": response
                    }
                )
                other_conv.append(
                    {
                        "role": "user",
                        "content": response
                    }
                )
                time.sleep(2)

    def _generate_response(self, conversation: List[Dict[str, str]], bot_name: str, system: bool, round_num: int) -> str:
        spinner = Halo(text='Loading...', spinner='dots')
        spinner.text = f"(#r{round_num}) {bot_name} loading..."
        spinner.start()
        response = ""

        try:
            conversation = [
                {"role": msg["role"], 
                "content": msg["content"]} for msg in conversation
            ]
        except Exception as e:
            spinner.fail("Failed")
            console.print_exception()
            sys.exit(1)

        try:
            response = self.clients[bot_name].generate(conversation, system_prompt)
            spinner.succeed(f"(#r{round_num}) {bot_name} done")

            panel = create_panel(
                    response,
                    title=f'{bot_name} (#r{round_num})',
                    timestamp=datetime.now(),
                    color="blue" if bot_name == "anthropic" else "green",
                )
            console.print(panel)

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            spinner.fail("Failed")
            console.print_exception()
            sys.exit(1)

        spinner.stop()
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
        help="Initial chat history"
    )

    parser.add_argument(
        "-s",
        "--system_prompt",
        action="store",
        default="data/prompts/simulation.txt",
        help="System prompt"
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

    if not os.path.exists(args.system_prompt):
        logger.error(f"System prompt file not found: {args.system_prompt}")
        sys.exit(1)
    
    with open(args.system_prompt, "r") as file:
        system_prompt = file.read()

    if args.chat and os.path.exists(args.chat):
        with open(args.chat, "r") as fp:
            try:
                data = json.load(fp)
                try:
                    if isinstance(data, list):
                        chat_history = data
                except ValidationError as e:
                    logger.error(f"Invalid chat history: {e}")
                    sys.exit(1)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading chat history: {e}")
                sys.exit(1)

    else:
        logger.warn("Using default conversation")
        chat_history = []

    logger.info(f"Starting conversation: {args.llm1}<->{args.llm2}")

    manager = ConversationManager(
        llm_1=args.llm1,
        llm_2=args.llm2,
        history=chat_history,
        system_prompt=system_prompt,
        rounds=args.rounds,
        output_file=args.output,
    )

    try:
        manager.converse()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
