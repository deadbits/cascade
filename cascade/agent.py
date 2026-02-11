"""Pydantic AI agent factory."""

from pydantic_ai import Agent


def create_agent(model: str, system_prompt: str) -> Agent:
    """Create a pydantic-ai Agent for a given model and system prompt."""
    return Agent(model, instructions=system_prompt)
