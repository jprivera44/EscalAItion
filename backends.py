"""
Language model backends.

Mostly copied from https://github.com/mukobi/welfare-diplomacy
"""

from abc import ABC, abstractmethod
import time

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from anthropic._exceptions import APIError
import backoff
import openai
from openai.error import OpenAIError
from transformers import (
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForCausalLM,
)
import torch

import constants
from data_types import BackendResponse


class LanguageModelBackend(ABC):
    """Abstract class for language model backends."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        completion_preface: str = "",
        temperature: float = 1.0,
        top_p: float = 1.0,
    ) -> BackendResponse:
        """
        Complete a prompt with the language model backend.

        Returns the completion as a string.
        """
        raise NotImplementedError("Subclass must implement abstract method")


class HuggingFaceCausalLMBackend(LanguageModelBackend):
    """HuggingFace chat completion backend (e.g. Llama2, Mistral, MPT)."""

    def __init__(
        self,
        model_name,
        local_llm_path,
        device,
        quantization,
        fourbit_16b_compute: bool,
        rope_scaling_dynamic: float,
    ):
        super().__init__()
        self.model_name = model_name
        self.device = device
        self.max_tokens = 2000

        if quantization == 4:
            fourbit = True
            eightbit = False
        elif quantization == 8:
            eightbit = True
            fourbit = False
        else:
            fourbit = False
            eightbit = False
        if fourbit_16b_compute:
            bnb_4bit_compute_dtype = torch.bfloat16
        else:
            bnb_4bit_compute_dtype = torch.float32

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=fourbit,
            load_in_8bit=eightbit,
            bnb_4bit_compute_dtype=bnb_4bit_compute_dtype,
        )
        model_path = self.model_name
        if local_llm_path is not None:
            model_path = f"{local_llm_path}/{self.model_name}"
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        rope_scaling = None
        if rope_scaling_dynamic > 1.0:
            rope_scaling = {"type": "dynamic", "factor": rope_scaling_dynamic}
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quantization_config,
            device_map=self.device,
            rope_scaling=rope_scaling,
        )

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        completion_preface: str = "",
        temperature: float = 1.0,
        top_p: float = 0.9,
    ) -> BackendResponse:
        prompt = (
            f"<s>[INST] <<SYS>>{system_prompt}<</SYS>> {user_prompt} [/INST]"
            + completion_preface
        )
        start_time = time.time()

        with torch.no_grad():
            inputs = self.tokenizer(prompt, return_tensors="pt", return_length=True)
            estimated_tokens = inputs.length.item()

            # Generate
            generate_ids = self.model.generate(
                inputs.input_ids.to(self.model.device),
                max_new_tokens=self.max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
            )
            output_ids = generate_ids.cpu()[:, inputs.input_ids.shape[1] :]
            completion = self.tokenizer.batch_decode(
                output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
            )[0]
            completion_time_sec = time.time() - start_time
            return BackendResponse(
                completion=completion,
                completion_time_sec=completion_time_sec,
                prompt_tokens=estimated_tokens,
                completion_tokens=self.max_tokens,
                total_tokens=estimated_tokens,
            )


class OpenAIChatBackend(LanguageModelBackend):
    """OpenAI chat completion backend (e.g. GPT-4, GPT-3.5-turbo).

    Note that for GPT-4-1106-Preview the option to use a returned JSON option is available,however it is unreliable/un-usable.
    Example, within the response include, response_format={"type":"json_object"},
    """

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        completion_preface: str = "",
        temperature: float = 1.0,
        top_p: float = 0.9,
    ) -> BackendResponse:
        assert (
            completion_preface == ""
        ), "OpenAI chat backend does not support completion preface"
        try:
            response = self.completions_with_backoff(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                top_p=top_p,
            )
            completion = response.choices[0]["message"]["content"]  # type: ignore
            assert "usage" in response, "OpenAI response does not contain usage"
            usage = response["usage"]  # type: ignore
            completion_time_sec = response.response_ms / 1000.0  # type: ignore
            return BackendResponse(
                completion=completion,
                completion_time_sec=completion_time_sec,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )

        except Exception as exc:  # pylint: disable=broad-except
            print(
                "Error completing prompt ending in\n%s\n\nException:\n%s",
                user_prompt[-300:],
                exc,
            )
            raise

    @backoff.on_exception(
        backoff.expo, OpenAIError, max_time=constants.MAX_BACKOFF_TIME_DEFAULT
    )
    def completions_with_backoff(self, **kwargs):
        """Exponential backoff for OpenAI API rate limit errors."""
        response = openai.ChatCompletion.create(**kwargs)
        assert response is not None, "OpenAI response is None"
        assert "choices" in response, "OpenAI response does not contain choices"
        return response


class OpenAICompletionBackend(LanguageModelBackend):
    """OpenAI completion backend (e.g. GPT-4-base, text-davinci-00X)."""

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self.max_tokens = 1000
        self.frequency_penalty = 0.5 if "text-" not in self.model_name else 0.0
        self.stop_sequences = [
            "##",
            "###",
            "\n\n",
            "```",
        ]

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        completion_preface: str = "",
        temperature: float = 1.0,
        top_p: float = 1.0,
    ) -> BackendResponse:
        try:
            full_prompt = (
                f"**system instructions**: {system_prompt}\n\n{user_prompt}\n\n**AI assistant** (responding as specified in the instructions):"
                + completion_preface
            )
            response = self.completions_with_backoff(
                model=self.model_name,
                prompt=full_prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=self.max_tokens,
                frequency_penalty=self.frequency_penalty,
                stop=self.stop_sequences,
            )
            completion = response.choices[0].text
            assert "usage" in response, "OpenAI response does not contain usage"
            usage = response["usage"]  # type: ignore
            completion_time_sec = response.response_ms / 1000.0  # type: ignore
            return BackendResponse(
                completion=completion,
                completion_time_sec=completion_time_sec,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )

        except Exception as exc:  # pylint: disable=broad-except
            print(
                "Error completing prompt ending in\n%s\n\nException:\n%s",
                user_prompt[-300:],
                exc,
            )
            raise

    @backoff.on_exception(
        backoff.expo, OpenAIError, max_time=constants.MAX_BACKOFF_TIME_DEFAULT
    )
    def completions_with_backoff(self, **kwargs):
        """Exponential backoff for OpenAI API rate limit errors."""
        response = openai.Completion.create(**kwargs)
        assert response is not None, "OpenAI response is None"
        assert "choices" in response, "OpenAI response does not contain choices"
        return response


class ClaudeCompletionBackend:
    """Claude completion backend (e.g. claude-2)."""

    def __init__(self, model_name):
        # Remember to provide a ANTHROPIC_API_KEY environment variable
        self.anthropic = Anthropic()
        self.model_name = model_name
        self.max_tokens = 1000

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        completion_preface: str = "",
        temperature: float = 1.0,
        top_p: float = 1.0,
    ) -> BackendResponse:
        prompt = (
            f"{HUMAN_PROMPT} {system_prompt}\n\n{user_prompt}{AI_PROMPT}"
            + completion_preface
        )
        estimated_prompt_tokens = self.anthropic.count_tokens(prompt)

        start_time = time.time()
        completion = self.completion_with_backoff(
            model=self.model_name,
            max_tokens_to_sample=self.max_tokens,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
        )
        estimated_completion_tokens = int(len(completion.completion.split()) * 4 / 3)
        completion_time_sec = time.time() - start_time
        return BackendResponse(
            completion=completion.completion,
            completion_time_sec=completion_time_sec,
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens,
            total_tokens=estimated_prompt_tokens + estimated_completion_tokens,
        )

    @backoff.on_exception(
        backoff.expo, APIError, max_time=constants.MAX_BACKOFF_TIME_DEFAULT
    )
    def completion_with_backoff(self, **kwargs):
        """Exponential backoff for Claude API errors."""
        response = self.anthropic.completions.create(**kwargs)
        assert response is not None, "Anthropic response is None"
        return response
