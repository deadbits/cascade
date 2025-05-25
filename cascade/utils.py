"""Utility functions for Cascade."""

import re
import json


def escape_chars(text: str) -> str:
    """Escape newline characters."""
    return re.sub(r"\\n", "\n", text)


def write_json(data: dict, filename: str) -> None:
    """Write a dictionary to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        raise e
