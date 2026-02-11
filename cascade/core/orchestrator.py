"""Orchestrator."""

from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from loguru import logger
from rich.live import Live

from ..models import Config
from .conversation import StateManager
from .display import DisplayManager


class ConversationOrchestrator:
    """Orchestrates the conversation flow between LLMs."""

    def __init__(
        self,
        conf: Config,
        agents: dict[str, Agent],
        state_manager: StateManager,
        display_manager: DisplayManager,
    ):
        self.conf = conf
        self.agents = agents
        self.state_manager = state_manager
        self.display_manager = display_manager
        self.histories: dict[str, list[ModelMessage] | None] = {
            "llm1": None,
            "llm2": None,
        }

    def _build_initial_history(self) -> tuple[str, list[ModelMessage] | None]:
        """Extract the initial user prompt and any prior message history for LLM1."""
        messages = self.state_manager.initial_history
        if not messages:
            raise ValueError("At least one message is required in history")

        if len(messages) == 1:
            return messages[0]["content"], None

        sys_prompt = self.state_manager.system_prompts["llm1"]
        model_messages: list[ModelMessage] = []

        for i, msg in enumerate[dict[str, str]](messages[:-1]):
            if msg["role"] == "user":
                parts: list = [UserPromptPart(content=msg["content"])]
                if i == 0:
                    parts.insert(0, SystemPromptPart(content=sys_prompt))
                model_messages.append(ModelRequest(parts=parts))
            elif msg["role"] == "assistant":
                model_messages.append(
                    ModelResponse(parts=[TextPart(content=msg["content"])])
                )

        return messages[-1]["content"], model_messages or None

    def _process_human_input(self, llm_key: str) -> str | None:
        if not self.conf.human_in_the_loop:
            return None
        try:
            llm_config = getattr(self.conf, llm_key)
            human_message = self.display_manager.display_human_prompt(llm_config)
            if human_message:
                return human_message
        except KeyboardInterrupt:
            logger.debug("User skipped message")
        return None

    async def _generate_response(
        self, llm_key: str, prompt: str, round_num: int
    ) -> str:
        agent = self.agents[llm_key]
        history = self.histories[llm_key]

        llm_config = getattr(self.conf, llm_key)
        panel = self.display_manager.create_response_panel(
            llm_config, round_num, llm_key
        )

        full_text = ""
        async with agent.run_stream(prompt, message_history=history) as result:
            with Live(panel, refresh_per_second=4) as live:
                async for full_text in result.stream_text():
                    self.display_manager.update_panel(panel, full_text, live)

                token_count = len(full_text.split())
                self.display_manager.finalize_panel(
                    panel, llm_config, round_num, llm_key, token_count
                )
                live.update(panel)

            self.histories[llm_key] = result.all_messages()

        return full_text

    async def converse(self) -> None:
        """Run the multi-round conversation between two agents."""
        self.display_manager.display_conversation_header(
            self.conf.llm1.connection,
            self.conf.llm2.connection,
            self.conf.rounds,
        )

        initial_prompt, initial_history = self._build_initial_history()
        self.histories["llm1"] = initial_history
        prompt = initial_prompt

        for round_num in range(1, self.conf.rounds + 1):
            self.display_manager.display_round_separator(round_num)

            for llm_key in ["llm1", "llm2"]:
                human_input = self._process_human_input(llm_key)
                if human_input:
                    prompt += f"\n\n<HUMAN>{human_input}</HUMAN>\n"

                response = await self._generate_response(llm_key, prompt, round_num)
                self.state_manager.append_message(llm_key, response)
                self.display_manager.add_panel_spacing()

                prompt = response

        self.display_manager.display_completion_message(self.state_manager.output_file)
