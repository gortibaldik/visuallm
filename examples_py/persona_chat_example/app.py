import copy
import json
import os

from datasets import DatasetDict, load_dataset
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from examples_py.persona_chat_example.create_app import (
    switch_persona_from_first_to_second_sentence,
)
from visuallm.components.generators.base import Generator
from visuallm.components.generators.huggingface import HuggingFaceGenerator
from visuallm.components.generators.openai import OpenAIGenerator

from .components.chat import get_persona_traits
from .create_app import create_app


def create_text_to_tokenizer(loaded_sample, target: str | None = None) -> str:
    text_to_tokenizer = " ".join(
        [
            s
            for part in [
                loaded_sample["personality"],
                loaded_sample["history"],
                [loaded_sample["user_message"]]
                if ("user_message" in loaded_sample)
                and (len(loaded_sample["user_message"].strip()) != 0)
                else [],
                [target] if target is not None else [],
            ]
            for s in part
        ]
    )
    return text_to_tokenizer


def create_text_to_tokenizer_one_step(loaded_sample, received_tokens: list[str]):
    sample = copy.deepcopy(loaded_sample)
    if len(received_tokens) > 0:
        received_tokens[0] = received_tokens[0].lstrip()
    sample["user_message"] = "".join(received_tokens)
    text_to_tokenizer = create_text_to_tokenizer(sample)
    return text_to_tokenizer


def retrieve_target_str(loaded_sample):
    return loaded_sample["candidates"][-1]


def create_text_to_tokenizer_openai(loaded_sample, target: str | None = None) -> str:
    model = "gpt-3.5-turbo-0613"
    system_traits = "You are a chatbot for the task where you try to impersonate a human who identifies himself with the following traits: "
    system_traits += " ".join(
        [
            switch_persona_from_first_to_second_sentence(sentence)
            for sentence in loaded_sample["personality"]
        ]
    )
    system_traits += " Your answers should be about a sentence long."
    history = copy.deepcopy(loaded_sample["history"])
    if ("user_message" in loaded_sample) and (
        len(loaded_sample["user_message"].strip()) != 0
    ):
        history.append(copy.deepcopy(loaded_sample["user_message"]))
    messages = [{"role": "system", "content": system_traits}]
    roles = ["user", "assistant"]
    for i, message in enumerate(history):
        messages.append({"role": roles[i % 2], "content": message})

    return json.dumps({"model": model, "messages": messages})


# load models
_dataset = load_dataset("bavard/personachat_truecased")
if not isinstance(_dataset, DatasetDict):
    raise TypeError("Only dataset and dataset dict are supported")
_tokenizer = AutoTokenizer.from_pretrained("gpt2")
_model = AutoModelForCausalLM.from_pretrained("gpt2")

_generator_choices: dict[str, Generator] = {}
generator = HuggingFaceGenerator(
    model=_model,
    tokenizer=_tokenizer,
    create_text_to_tokenizer=create_text_to_tokenizer,
    create_text_to_tokenizer_one_step=create_text_to_tokenizer_one_step,
    retrieve_target_str=retrieve_target_str,
)
_generator_choices["gpt2"] = generator

if "OPENAI_API_KEY" in os.environ:
    open_ai_generator = OpenAIGenerator(
        create_text_to_tokenizer_openai, retrieve_target_str=retrieve_target_str
    )
    _generator_choices["gpt-3.5-turbo-0613"] = open_ai_generator

app = create_app(
    _dataset,
    _generator_choices,
    get_persona_traits=get_persona_traits,
    next_token_generator_choices={"gpt2": _generator_choices["gpt2"]},
)


# TODO: collapsible elements (i.e. element in element) - after merge request
# TODO: add new text input to the chat component
