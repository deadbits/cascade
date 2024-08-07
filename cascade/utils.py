"""Utility functions for Cascade."""
import re
import json

from datetime import datetime
from typing import Optional
from rich.markdown import Markdown
from rich.panel import Panel


def escape_chars(text: str) -> str:
    """Escape newline characters."""
    return re.sub(r'\\n', '\n', text)

def create_panel(
    content: str,
    title: str,
    timestamp: Optional[datetime] = None,
    color: str = "white"
) -> Panel:
    """Create a rich panel with a title and optional timestamp."""
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else ""
    panel_title = f"[bold {color}]{title}[/bold {color}] - {timestamp_str}"
    return Panel(Markdown(content), title=panel_title, expand=False)

def write_json(data: dict, filename: str) -> None:
    """Write a dictionary to a JSON file."""
    try:
        with open(filename, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        raise e
