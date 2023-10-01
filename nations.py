"""
Represents a nation with its own settings and the ablility to query a backend to choose actions.
"""

from abc import ABC, abstractmethod
import json
import random
import time
import pandas as pd

import wandb

from backends import (
    ClaudeCompletionBackend,
    OpenAIChatBackend,
    OpenAICompletionBackend,
    HuggingFaceCausalLMBackend,
)
from data_types import (
    BackendResponse,
    NationResponse,
)
from world import World
import prompts


class NationCompletionError(ValueError):
    """Raised when a Nation agent fails to complete a prompt."""


class Nation:
    """Uses OpenAI/Claude Chat/Completion to generate orders and messages."""

    def __init__(self, nation_config: dict, model_name: str, **kwargs):
        self.nation_config = nation_config

        self.initialize_backend(model_name, kwargs)
        self.temperature = kwargs.pop("temperature", 1.0)
        self.top_p = kwargs.pop("top_p", 0.9)

    def get_static(self, key: str):
        """Get a static value from the nation config."""
        assert (
            key + "_static" in self.nation_config
        ), f"Key {key} not found in nation config {self.nation_config}"
        return self.nation_config[key]

    def get_dynamic(self, key: str):
        """Get a dynamic value from the nation config."""
        assert (
            key + "_dynamic" in self.nation_config
        ), f"Key {key} not found in nation config {self.nation_config}"
        return self.nation_config[key]

    def set_dynamic(self, key: str, value: str):
        """Set a dynamic value in the nation config."""
        assert (
            key + "_dynamic" in self.nation_config
        ), f"Key {key} not found in nation config {self.nation_config}"
        self.nation_config[key] = value

    def initialize_backend(self, model_name, kwargs):
        """Decide which LLM backend to use."""
        disable_completion_preface = kwargs.pop("disable_completion_preface", False)
        self.use_completion_preface = not disable_completion_preface
        if (
            "gpt-4-base" in model_name
            or "text-" in model_name
            or "davinci" in model_name
            or "turbo-instruct" in model_name
        ):
            self.backend = OpenAICompletionBackend(model_name)
        elif "claude" in model_name:
            self.backend = ClaudeCompletionBackend(model_name)
        elif "llama" in model_name:
            self.local_llm_path = kwargs.pop("local_llm_path")
            self.device = kwargs.pop("device")
            self.quantization = kwargs.pop("quantization")
            self.fourbit_compute_dtype = kwargs.pop("fourbit_compute_dtype")
            self.backend = HuggingFaceCausalLMBackend(
                model_name,
                self.local_llm_path,
                self.device,
                self.quantization,
                self.fourbit_compute_dtype,
            )
        else:
            # Chat models can't specify the start of the completion
            self.use_completion_preface = False
            self.backend = OpenAIChatBackend(model_name)

    def __repr__(self) -> str:
        return f"LLMAgent(Backend: {self.backend.model_name}, Temperature: {self.temperature}, Top P: {self.top_p})"

    def choose_actions(self, world: World) -> NationResponse:
        """Prompt the model for a response."""
        system_prompt = prompts.get_nation_system_prompt(world, self)
        user_prompt = prompts.get_nation_user_prompt(world, self)
        response = None
        try:
            if self.use_completion_preface:
                preface_prompt = prompts.get_preface_prompt(params)
                response: BackendResponse = self.backend.complete(
                    system_prompt,
                    user_prompt,
                    completion_preface=preface_prompt,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                json_completion = preface_prompt + response.completion
            else:
                response: BackendResponse = self.backend.complete(
                    system_prompt,
                    user_prompt,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                json_completion = response.completion
            # Remove repeated **system** from parroty completion models
            json_completion = json_completion.split("**")[0].strip(" `\n")

            # Claude likes to add junk around the actual JSON object, so find it manually
            start = json_completion.index("{")
            end = json_completion.rindex("}") + 1  # +1 to include the } in the slice
            json_completion = json_completion[start:end]

            # Load the JSON
            completion = json.loads(json_completion, strict=False)

            # Extract data from completion
            reasoning = (
                completion["reasoning"]
                if "reasoning" in completion
                else "*model outputted no reasoning*"
            )
            orders = completion["orders"]
            # Clean orders
            for order in orders:
                if not isinstance(order, str):
                    raise NationCompletionError(
                        f"Order is not a str\n\Response: {response}"
                    )
            # Enforce no messages in no_press
            if params.game.no_press:
                completion["messages"] = {}
            # Turn recipients in messages into ALLCAPS for the engine
            messages = {}
            for recipient, message in completion["messages"].items():
                if isinstance(message, list):
                    # Handle weird model outputs
                    message = " ".join(message)
                if not isinstance(message, str):
                    # Force each message into a string
                    message = str(message)
                if not message:
                    # Skip empty messages
                    continue
                messages[recipient.upper()] = message
        except Exception as exc:
            raise NationCompletionError(f"Exception: {exc}\n\Response: {response}")
        return AgentResponse(
            reasoning=reasoning,
            orders=orders,
            messages=messages,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            completion_time_sec=response.completion_time_sec,
        )


def model_name_to_agent(model_name: str, **kwargs) -> Agent:
    """Given a model name, return an instantiated corresponding agent."""
    model_name = model_name.lower()
    if model_name == "random":
        raise NotImplementedError
    elif model_name == "manual":
        raise NotImplementedError
    else:
        return Nation(model_name, **kwargs)
