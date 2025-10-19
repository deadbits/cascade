"""Display manager."""

from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box
from rich.live import Live
from rich.text import Text
from datetime import datetime

from cascade.models import LLMConfig


class DisplayManager:
    """Manages the rich UI."""

    def __init__(self):
        self.console = Console()

        self.llm_colors = {
            "llm1": {
                "border": "bright_cyan",
                "title": "cyan",
                "bg": "on grey11",
                "box": box.HEAVY,
            },
            "llm2": {
                "border": "bright_magenta",
                "title": "magenta",
                "bg": "on grey11",
                "box": box.DOUBLE,
            },
        }

    def create_response_panel(
        self, llm_config: LLMConfig, round_num: int, llm_key: str
    ) -> Panel:
        """Create a panel for displaying LLM responses."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = self.llm_colors[llm_key]

        title = f"[{colors['title']}]{llm_config.connection}[/] [dim]#r{round_num}[/] [grey50]{timestamp}[/] [yellow]●[/] [dim]streaming...[/]"

        return Panel(
            Group(),
            title=title,
            border_style=colors["border"],
            box=colors["box"],
            expand=False,
            padding=(1, 2),
        )

    def update_panel(self, panel: Panel, content: str, live: Live) -> None:
        """Update the panel with new content."""
        md = Markdown(content, code_theme="monokai", inline_code_theme="monokai")
        panel.renderable = Group(md)
        live.update(panel)

    def finalize_panel(
        self,
        panel: Panel,
        llm_config: LLMConfig,
        round_num: int,
        llm_key: str,
        token_count: int,
    ) -> None:
        """Update panel title when streaming is complete."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = self.llm_colors[llm_key]

        final_title = f"[{colors['title']}]{llm_config.connection}[/] [dim]#r{round_num}[/] [grey50]{timestamp}[/] [green]✓[/] [dim]{token_count} tokens[/]"
        panel.title = final_title

    def display_conversation_header(
        self, llm1_name: str, llm2_name: str, total_rounds: int
    ) -> None:
        """Display conversation header."""
        header = Text()
        header.append("CONVERSATION: ", style="bold bright_white")
        header.append(f"{llm1_name}", style="bright_cyan")
        header.append(" ⇄ ", style="dim")
        header.append(f"{llm2_name}", style="bright_magenta")
        header.append(f" [{total_rounds} rounds]", style="dim")

        header_panel = Panel(
            header,
            box=box.SQUARE,
            border_style="white",
            padding=(0, 1),
        )
        self.console.print(header_panel)
        self.console.print()

    def display_round_separator(self, round_num: int) -> None:
        """Display separator between rounds."""
        separator = Text(f" ROUND {round_num} ", style="bold black on white")
        separator_panel = Panel(
            separator,
            box=box.MINIMAL,
            border_style="dim",
            padding=(0, 0),
        )
        self.console.print(separator_panel)

    def add_panel_spacing(self) -> None:
        """Add spacing between panels."""
        self.console.print()

    def display_human_prompt(self, llm_config: LLMConfig) -> str:
        """Display prompt for human input."""
        prompt_text = Text()
        prompt_text.append("HUMAN INPUT ", style="bold yellow")
        prompt_text.append("for ", style="dim")
        prompt_text.append(f"{llm_config.connection}", style="bright_white")
        prompt_text.append(" (press Enter to skip): ", style="dim")

        self.console.print()
        self.console.print(prompt_text, end="")
        return input().strip()

    def display_completion_message(self, output_file: str) -> None:
        """Display conversation completion message."""
        completion_text = Text()
        completion_text.append("CONVERSATION COMPLETE ", style="bold green")
        completion_text.append("| Saved to: ", style="dim")
        completion_text.append(f"{output_file}", style="bright_white")

        completion_panel = Panel(
            completion_text,
            box=box.SQUARE,
            border_style="green",
            padding=(0, 1),
        )
        self.console.print()
        self.console.print(completion_panel)
