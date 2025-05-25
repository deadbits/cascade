"""Base classes for LLM wrappers."""

from abc import ABC, abstractmethod
from typing import Generator, List, Optional

from cascade.models import Message


class BaseLLMWrapper(ABC):
    """Abstract base class for LLM wrappers."""

    @abstractmethod
    def __init__(self, model: str):
        """Initialize the LLM wrapper.

        Args:
            model: The model identifier to use
        """
        self.model = model
        self.name = self.__class__.__name__.replace("Wrapper", "").lower()

    @abstractmethod
    def generate_stream(
        self, messages: List[Message], system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Generate a streaming response.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt

        Yields:
            Chunks of the generated response
        """
        pass
