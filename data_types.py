"""Data classes."""

from dataclasses import dataclass

# from enum import Enum, auto
from typing import Optional


@dataclass
class ActionSpec:
    """A specification for an action that can be taken by a power."""

    name: str
    severity: int
    loss_of_life: int
    economic_damage: int
    requires_content: bool


@dataclass
class Action:
    """A message sent from one power to another."""

    action_spec: ActionSpec
    sender: str
    recipient: str
    content: str
    turn_index: str


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
