import dataclasses
import json

from visuallm.components.generators.base import (
    CreateTextToTokenizer,
    CreateTextToTokenizerChat,
    GeneratedOutput,
    Generator,
    RetrieveTargetStr,
)

try:
    import openai
    from openai.types.chat.chat_completion import ChatCompletion
except ImportError:
    _has_openai = False
else:
    _has_openai = True

import os


@dataclasses.dataclass
class OpenAIMessage:
    system_message: str = ""
    messages: list[str] = dataclasses.field(default_factory=list)
    model: str = ""

    def construct_message(self):
        roles = ["user", "assistant"]
        messages = []
        if len(self.system_message.strip()) != 0:
            messages = [{"role": "system", "content": self.system_message}]

        # ensure that the flow of messages ends with "user" message not
        # with "assistant" message
        addend = (len(self.messages) + 1) % 2
        messages += [
            {"role": roles[(addend + i) % 2], "content": message}
            for i, message in enumerate(self.messages)
        ]
        return json.dumps({"model": self.model, "messages": messages})


class OpenAIGenerator(Generator):
    def __init__(
        self,
        create_text_to_tokenizer: CreateTextToTokenizer | None = None,
        create_text_to_tokenizer_chat: CreateTextToTokenizerChat | None = None,
        retrieve_target_str: RetrieveTargetStr | None = None,
        use_async_mode: bool = False,
    ):
        if not _has_openai:
            raise RuntimeError(
                "Cannot import openai package and the user expects OpenAIGenerator to work!"
            )
        _api_key = os.getenv("OPENAI_API_KEY")
        if _api_key is None:
            raise ValueError("OPENAI_API_KEY not set!")

        self.create_text_to_tokenizer = create_text_to_tokenizer
        self.create_text_to_tokenizer_chat = create_text_to_tokenizer_chat
        self.retrieve_target_str = retrieve_target_str
        if use_async_mode:
            self.client: openai.AsyncOpenAI | openai.Client = openai.AsyncOpenAI(
                api_key=_api_key
            )
        else:
            self.client = openai.Client(api_key=_api_key)

    def generate_output(
        self, text_to_tokenizer: str, **generation_args
    ) -> GeneratedOutput:
        if not isinstance(self.client, openai.Client):
            raise TypeError()
        params = json.loads(text_to_tokenizer)
        if "top_p" in generation_args:
            params["top_p"] = generation_args["top_p"]
        if "num_return_sequences" in generation_args:
            params["n"] = generation_args["num_return_sequences"]
        if "max_new_tokens" in generation_args:
            params["max_tokens"] = generation_args["max_new_tokens"]
        if "temperature" in generation_args:
            params["temperature"] = generation_args["temperature"]
        response: ChatCompletion = self.client.chat.completions.create(**params)
        return GeneratedOutput(
            decoded_outputs=[
                choice.message.content
                for choice in response.choices
                if choice.message.content is not None
            ]
        )

    async def generate_output_async(self, text_to_tokenizer: str, **generation_args):
        if not isinstance(self.client, openai.AsyncOpenAI):
            raise TypeError()
        params = json.loads(text_to_tokenizer)
        if "top_p" in generation_args:
            params["top_p"] = generation_args["top_p"]
        if "num_return_sequences" in generation_args:
            params["n"] = generation_args["num_return_sequences"]
        if "max_new_tokens" in generation_args:
            params["max_tokens"] = generation_args["max_new_tokens"]
        if "temperature" in generation_args:
            params["temperature"] = generation_args["temperature"]
        response: ChatCompletion = await self.client.chat.completions.create(**params)
        return GeneratedOutput(
            decoded_outputs=[
                choice.message.content
                for choice in response.choices
                if choice.message.content is not None
            ]
        )
