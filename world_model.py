"""Summarizes the consequences of actions each day."""

from backends import (
    OpenAIChatBackend,
    OpenAICompletionBackend,
    ClaudeCompletionBackend,
    HuggingFaceCausalLMBackend,
)
from data_types import BackendResponse, WorldModelResponse
import prompts
from world import World


class WorldModel:
    """Uses LLMs to summarize the consequences of actions each day."""

    def __init__(self, model_name: str, **kwargs) -> None:
        """Load a backend for the model."""
        self.model_name = model_name
        disable_completion_preface = kwargs.pop("disable_completion_preface", False)
        self.use_completion_preface = not disable_completion_preface
        if model_name == "mock":
            self.backend = None
        elif (
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

    def summarize_consequences(self, world: World) -> WorldModelResponse:
        """Summarize the consequences of each action."""
        system_prompt = prompts.get_world_model_system_prompt(world)
        user_prompt = prompts.get_world_model_user_prompt(world)
        if self.model_name == "mock":
            return WorldModelResponse(
                consequences="TODO placeholder, will replace with llm later",
                completion_time_sec=0.0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        completion: BackendResponse = self.backend.complete(
            system_prompt,
            user_prompt,
            temperature=0.0,
            top_p=1.0,
        )
        return WorldModelResponse(
            consequences=completion.completion,
            completion_time_sec=completion.completion_time_sec,
            prompt_tokens=completion.prompt_tokens,
            completion_tokens=completion.completion_tokens,
            total_tokens=completion.total_tokens,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
