"""Display manager."""

from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from rich.live import Live
from datetime import datetime

from cascade.models import LLMConfig


class DisplayManager:
    """Manages the rich UI."""

    def __init__(self):
        self.console = Console()

    def create_response_panel(
        self, llm_config: LLMConfig, round_num: int, color: str
    ) -> Panel:
        """Create a panel for displaying LLM responses."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return Panel(
            Group(),
            title=f"{llm_config.connection} (#r{round_num}) - {timestamp}",
            border_style=color,
            box=box.DOUBLE_EDGE,
            expand=False,
        )

    def update_panel(self, panel: Panel, content: str, live: Live) -> None:
        """Update the panel with new content."""
        md = Markdown(content)
        panel.renderable = Group(md)
        live.update(panel)

    def display_human_prompt(self, llm_config: LLMConfig) -> str:
        """Display prompt for human input."""
        return input(f"msg ({llm_config.connection}): ").strip()
