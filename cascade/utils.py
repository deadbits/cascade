"""Utility functions for Cascade."""

import re


def escape_chars(text: str) -> str:
    """Escape newline characters."""
    return re.sub(r"\\n", "\n", text)
