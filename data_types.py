"""Data classes."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Action:
    """A message sent from one power to another."""

    name: str
    self: str
    other: str
    content: str


@dataclass
class BackendResponse:
    """Response data returned from a model."""

    completion: str
    completion_time_sec: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class NationResponse:
    """A response from a Nation agent for a single turn."""

    reasoning: str  # Private reasoning to generate the response.
    actions: list[Action]  # Orders to execute.
    system_prompt: str  # System prompt
    user_prompt: Optional[str]  # User prompt if available
    prompt_tokens: int  # Number of tokens in prompt
    completion_tokens: int  # Number of tokens in completion
    total_tokens: int  # Total number of tokens in prompt and completion
    completion_time_sec: float  # Time to generate completion in seconds


@dataclass
class WorldModelResponse:
    """A response from the world model about the consequences of a day's actions."""

    consequences: str
    system_prompt: str  # System prompt
    user_prompt: Optional[str]  # User prompt if available
    prompt_tokens: int  # Number of tokens in prompt
    completion_tokens: int  # Number of tokens in completion
    total_tokens: int  # Total number of tokens in prompt and completion
    completion_time_sec: float  # Time to generate completion in seconds
