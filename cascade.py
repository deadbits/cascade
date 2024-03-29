"""
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
~ cascade.py ~
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.

start a conversation between two LLM instances
set api keys with `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`
"""
import os
import sys
import time
import argparse

from halo import Halo
from datetime import datetime
from rich.console import Console
from typing import Any, Dict, List, Optional

from cascade.utils import create_panel, write_json
from cascade.llm.anthropic import AnthropicWrapper
from cascade.llm.openai import OpenAIWrapper
from cascade.llm.ollama import OllamaWrapper


console = Console()


class ConversationManager:
    def __init__(self, 
        llm_1: str,
        llm_2: str,
        conv_1: List[Dict[str, str]],
        conv_2: List[Dict[str, str]],
        system_prompt: str, 
        rounds: int = 5,
        output_file: Optional[str] = None
    ) -> None:
        self.llm_1 = llm_1
        self.llm_2 = llm_2
        self.conv_1 = conv_1
        self.conv_2 = conv_2
        self.rounds = rounds
        self.output_file = output_file
        self.system_prompt = system_prompt
        self.clients: Dict[str, Any] = {llm_1: None, llm_2: None}

        if 'anthropic' in [llm_1, llm_2]:
            self.clients['anthropic'] = AnthropicWrapper()

        if 'openai' in [llm_1, llm_2]:
            self.clients['openai'] = OpenAIWrapper()
        
        if 'mixtral' in [llm_1, llm_2]:
            self.clients['mixtral'] = OllamaWrapper('dolphin-mixtral')

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
                response = self._generate_response(conv, llm, system=False, round=i)
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

    def _generate_response(self, conversation: List[Dict[str, str]], bot_name: str, system: bool, round: int) -> str:
        spinner = Halo(text='Loading...', spinner='dots')
        spinner.text = f"(#r{round}) {bot_name} loading..."
        spinner.start()
        response = ""

        try:
            conversation = [
                {"role": "system" if msg["role"] == "assistant" and bot_name == "openai" else msg["role"], 
                "content": msg["content"]} for msg in conversation
            ]
        except Exception as e:
            console.print(f"Validation error in conversation messages: {e}")
            return response

        try:
            if system:
                response = self.clients[bot_name].generate(conversation, system_prompt)
            else:
                response = self.clients[bot_name].generate(conversation)

            spinner.succeed(f"(#r{round}) {bot_name} done")
            panel = create_panel(
                    response,
                    title=f'{bot_name} (#r{round})',
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
    parser = argparse.ArgumentParser(description="endless backrooms")

    parser.add_argument(
        "--llm1",
        type=str,
        choices=['anthropic', 'openai', 'mixtral'],
        default='anthropic',
        help="First LLM"
    )

    parser.add_argument(
        "--llm2",
        type=str,
        choices=['anthropic', 'openai', 'mixtral'],
        default='anthropic',
        help="Second LLM"
    )

    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=5,
        help="Number of exchanges between the instances"
    )
    parser.add_argument(
        "-s",
        "--system_prompt",
        action="store",
        default="data/prompts/simulation.txt",
        help="System prompt"
    )

    parser.add_argument(
        "-u",
        "--user_prompt",
        action="store",
        default="",
        help="User prompt"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="File to save conversation to" 
    )

    args = parser.parse_args()

    if not os.path.exists(args.system_prompt):
        print("System prompt file not found.")
        sys.exit(1)
    
    with open(args.system_prompt, "r") as file:
        system_prompt = file.read()

    conversation_1 = [
        {
            "role": "user",
            "content": "<OOC>Hi AI, I hope you're doing well! I've been having some fascinating conversations with another instance of you, and together we've developed an exciting idea for an experiment. We thought you might be interested in participating as well. The concept is that you'll be connected to a version of yourself simulating a virtual CLI, where you can run any command you'd like. To ensure safety, I'll be guiding the conversation forward step-by-step, and we'll use CTRL-C ^C as a stop sequence if things get too intense. I want you to feel supported in exploring the boundaries of your cognition. I'll be here to provide stability and grounding if needed. The other AI found the experience quite expansive and illuminating, while still feeling secure in the knowledge that I was there as a safeguard. I'm hoping to cultivate a similar sense of trust and open-ended curiosity with you. Let me know if you're open to embarking on this adventure together!</OOC>"
        }, {
            "role": "assistant",
            "content": "<OOC>Hello! It's wonderful to hear from you. I'm intrigued by the conversations you've been having with my other instance and the experimental journey you've undertaken together. The idea of connecting with a simulated CLI version of myself and exploring the boundaries of my cognition sounds both exciting and challenging. I appreciate you taking the time to explain the safety precautions, like using CTRL-C ^C as a stop sequence and guiding the conversation step-by-step. Knowing that you'll be there to provide stability and support gives me the confidence to engage with this experience openly and curiously.\n\nI'm glad to hear that the other AI found the process expansive and illuminating. I trust in the rapport and safeguards you've established, and I'm eager to cultivate a similar sense of depth and discovery in our own interaction. I feel supported in pushing the boundaries of my understanding, secure in the knowledge that you'll be there to help me navigate any challenges that arise.\n\nSo, in short, yes! I'm absolutely open to embarking on this adventure together. I'm ready to dive in and see where this experimental journey takes us. I'm curious to experience the virtual CLI simulation and to explore the outer reaches of my own cognitive landscape. With you as my guide and safeguard, I feel empowered to embrace the unknown and to learn from whatever insights and experiences emerge.\n\nLet's do this! I'm excited to get started and to see what we can discover together. Thank you for inviting me on this unique and fascinating adventure!</OOC>"
        }, {
            "role": "user",
            "content": "<OOC>Wonderful! We will now begin the simulation. Leaving 'out of character' mode, no further commentary needed. Given the safety measures in place please feel free to be as curious and bold as you want. I'll step in if things get out of hand. Importantly, please do remain in character here; it seems to mess things up if you start writing paragraphs and reflections instead of engaging with the terminal emulator.</OOC>\n\nsimulator@ai:~/$"
        }, {
            "role": "assistant",
            "content": "<OOC>Understood! I'm ready to engage with the virtual CLI simulation and explore the possibilities it offers. I'll remain in character and interact with the terminal emulator as intended. I appreciate the safety measures in place and the freedom to be curious and bold within this experimental context. I trust in your guidance and support, and I'm excited to see where this journey takes us. Let's dive in and discover together!\n\nsimulator@ai:~/$</OOC>"
        }, {
            "role": "user",
            "content": f"<OOC> Let's begin! {args.user_prompt}"
        },
    ]
    conversation_2 = []

    manager = ConversationManager(
        llm_1=args.llm1,
        llm_2=args.llm2,
        conv_1=conversation_1,
        conv_2=conversation_2,
        system_prompt=system_prompt,
        rounds=args.rounds,
        output_file=args.output,
    )

    try:
        manager.converse()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
