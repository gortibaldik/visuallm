import math
import secrets
from typing import Any

from visuallm.components.generators.base import GeneratedOutput, Generator, LoadedSample
from visuallm.components.NextTokenPredictionComponent import (
    NextTokenPredictionInterface,
)

EXCEPTION_MESSAGE = "RAISE EXCEPTION"


class GeneratorStub(Generator, NextTokenPredictionInterface):

    """Dummy generator with few well defined options invoked through messages.

    Each dataset sample must contain 2 fields:
    "test": string
    "target": stringg
    """

    def __init__(self):
        self.token_step = 0

    def create_text_to_tokenizer_chat(self, loaded_sample: LoadedSample) -> str:
        text = loaded_sample["user_message"]
        if text == EXCEPTION_MESSAGE:
            raise ValueError("Exception raised during generation!")

        return text

    def create_text_to_tokenizer(
        self, loaded_sample: dict[str, Any], target: Any | None = None
    ) -> str:
        """The returned text is just the old text."""
        if not isinstance(loaded_sample, dict):
            raise TypeError()
        text = None
        if "text" in loaded_sample:
            text = loaded_sample["text"]

        if text is None:
            raise TypeError()

        if text == EXCEPTION_MESSAGE:
            raise ValueError("Exception raised during generation!")

        return text

    def one_step_prediction(self, text_to_tokenizer: str) -> list[tuple[float, str]]:
        vals = [
            (math.exp(secrets.randbelow(int(1e6)) / 1e6), f"word_{i}")
            for i in range(10)
        ]
        total_sum = sum(v[0] for v in vals)
        return sorted(((v[0] / total_sum * 100, v[1]) for v in vals), reverse=True)

    def convert_token_to_string(self, token: str):
        return token

    def create_text_to_tokenizer_one_step(
        self, loaded_sample: Any, received_tokens: list[str]
    ):
        return loaded_sample["text"] + "".join(received_tokens)

    def retrieve_target_str(self, loaded_sample: dict[str, Any]) -> str:
        if not isinstance(loaded_sample, dict):
            raise TypeError()
        if "target" not in loaded_sample:
            raise TypeError()

        return loaded_sample["target"]

    def generate_output(self, text_to_tokenizer: str, **kwargs):
        return GeneratedOutput(
            decoded_outputs=[f"generated text: '{text_to_tokenizer}'"]
        )
