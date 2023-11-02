import json

from visuallm.components.generators.base import (
    CreateTextToTokenizer,
    GeneratedOutput,
    Generator,
    RetrieveTargetStr,
)

try:
    import openai
except ImportError:
    _has_openai = False
else:
    _has_openai = True

import os


class OpenAIGenerator(Generator):
    def __init__(
        self,
        create_text_to_tokenizer: CreateTextToTokenizer,
        retrieve_target_str: RetrieveTargetStr,
    ):
        if not _has_openai:
            raise RuntimeError(
                "Cannot import openai package and the user expects OpenAIGenerator to work!"
            )
        self._api_key = os.getenv("OPENAI_API_KEY")
        if self._api_key is None:
            raise ValueError("OPENAI_API_KEY not set!")

        self.create_text_to_tokenizer = create_text_to_tokenizer
        self.retrieve_target_str = retrieve_target_str
        openai.api_key = self._api_key

    def generate_output(
        self, text_to_tokenizer: str, **generation_args
    ) -> GeneratedOutput:
        params = json.loads(text_to_tokenizer)
        # params = copy.deepcopy(text_to_tokenizer)
        if "top_p" in generation_args:
            params["top_p"] = generation_args["top_p"]
        if "num_return_sequences" in generation_args:
            params["n"] = generation_args["num_return_sequences"]
        if "max_new_tokens" in generation_args:
            params["max_tokens"] = generation_args["max_new_tokens"]
        if "temperature" in generation_args:
            params["temperature"] = generation_args["temperature"]
        response = openai.ChatCompletion.create(**params)
        return GeneratedOutput(
            decoded_outputs=[choice["message"]["content"] for choice in response["choices"]]  # type: ignore
        )
