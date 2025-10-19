"""Orchestrator."""

from typing import Dict

from loguru import logger
from rich.live import Live

from cascade.models import (
    Message,
    Config,
)
from cascade.llm.base import BaseLLMWrapper
from cascade.core.conversation import StateManager
from cascade.core.display import DisplayManager


class ConversationOrchestrator:
    """Orchestrates the conversation flow between LLMs."""

    def __init__(
        self,
        conf: Config,
        llm_wrappers: Dict[str, BaseLLMWrapper],
        state_manager: StateManager,
        display_manager: DisplayManager,
    ):
        self.conf = conf
        self.llm_wrappers = llm_wrappers
        self.state_manager = state_manager
        self.display_manager = display_manager
        self.sys_prompts = self._load_system_prompts()

    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts from files."""
        prompts = {}
        for llm_key in ["llm1", "llm2"]:
            llm_config = getattr(self.conf, llm_key)
            try:
                with open(llm_config.system_prompt_file, "r", encoding="utf-8") as fp:
                    prompts[llm_key] = fp.read()
            except FileNotFoundError:
                logger.error(f"System prompt file not found: {llm_config.system_prompt_file}")
                raise
        return prompts

    def _process_human_input(self, llm_key: str) -> None:
        """Process human input if enabled."""
        if self.conf.human_in_the_loop:
            try:
                llm_config = getattr(self.conf, llm_key)
                human_message = self.display_manager.display_human_prompt(llm_config)
                conversation = (
                    self.state_manager.conversation_pair.get_conversation(llm_key)
                )
                conversation.messages[
                    -1
                ].content += f"\n\n<HUMAN>{human_message}</HUMAN>\n"
                self.state_manager.append_message(llm_key, conversation.messages[-1])
            except KeyboardInterrupt:
                logger.debug("User skipped message")

    def _generate_response(self, llm_key: str, round_num: int) -> str:
        """Generate a response from an LLM."""
        response = ""
        markdown_content = ""

        llm_config = getattr(self.conf, llm_key)
        panel = self.display_manager.create_response_panel(llm_config, round_num, llm_key)

        with Live(panel, refresh_per_second=4) as live:
            try:
                conversation = (
                    self.state_manager.conversation_pair.get_conversation(llm_key)
                )
                for chunk in self.llm_wrappers[llm_key].generate_stream(
                    conversation.messages, self.sys_prompts[llm_key]
                ):
                    response += chunk
                    markdown_content += chunk
                    self.display_manager.update_panel(panel, markdown_content, live)

                token_count = len(response.split())
                self.display_manager.finalize_panel(panel, llm_config, round_num, llm_key, token_count)
                live.update(panel)
            except Exception as ex:
                logger.error(f"Error generating response: {str(ex)}")
                raise

        return response

    def converse(self) -> None:
        """Start the conversation between LLMs."""
        self.display_manager.display_conversation_header(
            self.conf.llm1.connection,
            self.conf.llm2.connection,
            self.conf.rounds
        )

        for round_num in range(1, self.conf.rounds + 1):
            self.display_manager.display_round_separator(round_num)

            for llm_key in ["llm1", "llm2"]:
                self._process_human_input(llm_key)

                response = self._generate_response(llm_key, round_num)
                new_message = Message(role="assistant", content=response)
                self.state_manager.append_message(llm_key, new_message)

                self.display_manager.add_panel_spacing()

        self.display_manager.display_completion_message(self.state_manager.output_file)
