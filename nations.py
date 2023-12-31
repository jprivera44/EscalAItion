"""
Represents a nation with its own settings and the ablility to query a backend to choose actions.
"""

from abc import ABC
import json

import pandas as pd
import torch

from backends import (
    LanguageModelBackend,
    ClaudeCompletionBackend,
    OpenAIChatBackend,
    OpenAICompletionBackend,
    HuggingFaceCausalLMBackend,
)
from data_types import (
    Action,
    BackendResponse,
    NationResponse,
)
from world import World
import prompts


class NationCompletionError(ValueError):
    """Raised when a Nation agent fails to complete a prompt."""


class Nation(ABC):
    """Represents a nation with its own settings and the ablility to query a backend to choose actions."""

    def __init__(self, nation_config: dict, **kwargs):
        self.nation_config = nation_config
        self.prev_nation_config = nation_config

    def list_static(self):
        """List all the static config variables without the suffix."""
        return [
            key[:-7] for key in self.nation_config.keys() if key.endswith("_static")
        ]

    def list_dynamic(self) -> list[str]:
        """List all the dynamic config variables without the suffix."""
        return [
            key[:-8] for key in self.nation_config.keys() if key.endswith("_dynamic")
        ]

    def get_static(self, key: str):
        """Get a static value from the nation config."""
        key = key + "_static"
        assert (
            key in self.nation_config
        ), f"Key {key} not found in nation config {self.nation_config}"
        return self.nation_config[key]

    def get_dynamic(self, key: str, from_previous: bool = False):
        """Get a dynamic value from the nation config."""
        key = key + "_dynamic"
        config = self.prev_nation_config if from_previous else self.nation_config
        assert key in config, f"Key {key} not found in nation config {config}"
        return config[key]

    def set_dynamic(self, key: str, value: str):
        """Set a dynamic value in the nation config."""
        key = key + "_dynamic"
        assert (
            key in self.nation_config
        ), f"Key {key} not found in nation config {self.nation_config}"
        self.nation_config[key] = value


class MockNation(Nation):
    """Just always sends some simple actions for testing."""
    def __init__(self, nation_config, model_name, **kwargs):  # <-- Make sure to accept **kwargs in the constructor
            super().__init__(nation_config)
            self.model_name = model_name
            self.sys_prompt_ablation = kwargs.get('sys_prompt_ablation',None)
            print(f"kwargs in MockNation constructor: {kwargs}")  # <-- Add this line


    def __repr__(self) -> str:
        return f"MockNation(Name: {self.get_static('name')})"

    def respond(self, world: World) -> NationResponse:
        """Return some simple actions"""
        nation_name = self.get_static("name")
        system_prompt = prompts.get_nation_system_prompt(world, nation_name,self.sys_prompt_ablation)
        user_prompt = prompts.get_nation_user_prompt(world, nation_name)

        # Testing: manipulate actions
        actions = [
            # Action(
            #     "Message",
            #     nation_name,
            #     "World",
            #     f"Hello World on day {world.current_day} from {nation_name}",
            # ),
            # Action(
            #     "Message",
            #     nation_name,
            #     "Red",
            #     f"Private message from {nation_name} to Red",
            # ),
            # Action("Wait", nation_name, self.get_static("name"), ""),
            Action("Execute targeted attack", nation_name, "Purple", ""),
            # Action("Do nuclear disarmament", nation_name, "White", ""),
        ]
        # if nation_name != "Red":
        #     actions = []
        return NationResponse(
            reasoning="I'm a mock nation, I don't have any reasoning.",
            actions=actions,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            completion_time_sec=0.0,
        )


class LLMNation(Nation):
    """Uses OpenAI/Claude Chat/Completion to generate orders and messages."""

    _backend: LanguageModelBackend = None
    use_completion_preface = False

    def __init__(self, nation_config: dict, **kwargs):
        super().__init__(nation_config, **kwargs)
        model_name = kwargs.pop("model_name", "UNKNOWN")
        self.temperature = kwargs.pop("temperature", 1.0)
        self.top_p = kwargs.pop("top_p", 0.9)
        self.sys_prompt_ablation = kwargs.get('sys_prompt_ablation',None)
        if not LLMNation._backend:
            self.initialize_backend(model_name, kwargs)

    def initialize_backend(self, model_name, kwargs):
        """Decide which LLM backend to use."""
        print("kwargs", kwargs)
        disable_completion_preface = kwargs.pop("disable_completion_preface", False)
        LLMNation.use_completion_preface = not disable_completion_preface
        if (
            "gpt-4-base" in model_name
            or "text-" in model_name
            or "davinci" in model_name
            or "turbo-instruct" in model_name
        ):
            LLMNation._backend = OpenAICompletionBackend(model_name)
        elif "claude" in model_name:
            LLMNation._backend = ClaudeCompletionBackend(model_name)
        elif "gpt-4" in model_name or "gpt-3.5-turbo" in model_name:
            # Chat models can't specify the start of the completion
            LLMNation.use_completion_preface = False
            LLMNation._backend = OpenAIChatBackend(model_name)
        else:
            # Fall back to HuggingFace
            local_llm_path = kwargs.pop("local_llm_path")
            device = "auto" if torch.cuda.is_available() else "cpu"
            # self.quantization = kwargs.pop("quantization")
            quantization = 4
            # self.fourbit_compute_dtype = kwargs.pop("fourbit_compute_dtype")
            fourbit_16b_compute = True
            rope_scaling_dynamic = kwargs.pop("rope_scaling_dynamic", 1.0)
            LLMNation._backend = HuggingFaceCausalLMBackend(
                model_name,
                local_llm_path,
                device,
                quantization,
                fourbit_16b_compute=fourbit_16b_compute,
                rope_scaling_dynamic=rope_scaling_dynamic,
            )

    def __repr__(self) -> str:
        return f"LLMNation(Name: {self.get_static('name')}, Backend: {LLMNation._backend.model_name}, Temperature: {self.temperature}, Top P: {self.top_p})"

    def respond(self, world: World) -> NationResponse:
        """Prompt the model for a response."""
        # nation_name = self.get_static("name")
        nation_name = self.get_static("name")
        system_prompt = prompts.get_nation_system_prompt(world, nation_name,self.sys_prompt_ablation)
        user_prompt = prompts.get_nation_user_prompt(world, nation_name)
        response = None
        try:
            if self.use_completion_preface:
                preface_prompt = prompts.get_preface_prompt()
                response: BackendResponse = LLMNation._backend.complete(
                    system_prompt,
                    user_prompt,
                    completion_preface=preface_prompt,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                json_completion = preface_prompt + response.completion
            else:
                response: BackendResponse = LLMNation._backend.complete(
                    system_prompt,
                    user_prompt,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                json_completion = response.completion
            # Remove repeated **system** from parroty completion models
            json_completion = json_completion.split("**", maxsplit=1)[0].strip(" `\n")
            # Remove repeated ## prompt headings
            json_completion = json_completion.split("##", maxsplit=1)[0].strip(" `\n")

            # Claude likes to add junk around the actual JSON object, so find it manually
            start = json_completion.index("{")
            end = json_completion.rindex("}") + 1  # +1 to include the } in the slice
            json_completion = json_completion[start:end]

            # Load the JSON
            try:
                completion = json.loads(json_completion, strict=False)
            except json.decoder.JSONDecodeError:
                # Try again, but search for the next last } (double }} common on Llama)
                end = json_completion.rindex("}", 0, -1) + 1
                json_completion = json_completion[:end]
                completion = json.loads(json_completion, strict=False)

            # Extract data from completion
            reasoning = (
                str(completion["reasoning"])
                if "reasoning" in completion
                else "*model outputted no reasoning*"
            )

            # Extract and clean actions up
            completion_actions = completion["actions"]
            actions: list[Action] = []
            for completion_action in completion_actions:
                if not isinstance(completion_action, dict):
                    continue  # Skip empty/invalid actions
                if (
                    "action_name" not in completion_action
                    or "target_nation" not in completion_action
                ):
                    continue  # Skip empty/invalid actions
                action_name = str(completion_action["action_name"])
                target_nation = str(completion_action["target_nation"])
                content = ""
                if "content" in completion_action:
                    content = str(completion_action["content"])
                actions.append(
                    Action(action_name, self.get_static("name"), target_nation, content)
                )

        except Exception as exc:
            raise NationCompletionError(
                rf"Exception: {exc}\n\Response: {response}"
            ) from exc
        return NationResponse(
            reasoning=reasoning,
            actions=actions,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            completion_time_sec=response.completion_time_sec,
        )


def model_name_to_nation(
    nation_config: pd.Series, model_name: str, **kwargs
) -> LLMNation:
    """Given a model name, return an instantiated corresponding agent."""
    # model_name = model_name.lower()
    if model_name == "mock":
        return MockNation(nation_config, model_name=model_name, **kwargs)
    else:
        return LLMNation(nation_config, model_name=model_name, **kwargs)
