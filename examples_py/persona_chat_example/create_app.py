import copy
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datasets import DatasetDict

try:
    import nltk
except ImportError:
    _has_nltk = False
else:
    _has_nltk = True

from visuallm import ComponentBase
from visuallm.components.GenerationComponent import GeneratedTextMetric, ProbsMetric
from visuallm.components.generators.base import (
    Generator,
)
from visuallm.components.generators.openai import OpenAIMessage
from visuallm.components.mixins.generation_selectors_mixin import (
    CheckBoxSelectorType,
    MinMaxSelectorType,
)
from visuallm.server import Server

from .components.chat import ChatComponent
from .components.generation import Generation
from .components.metrics import F1Score, Perplexity
from .components.next_token_prediction import NextTokenPrediction
from .components.visualization import Visualization

forms = {
    "am": "are",
    "Am": "Are",
    "are": "am",
    "Are": "Am",
    "i": "you",
    "I": "You",
    "you": "i",
    "You": "I",
    "my": "your",
    "My": "Your",
    "your": "my",
    "Your": "My",
    "yours": "mine",
    "Yours": "Mine",
    "Mine": "Yours",
    "mine": "yours",
    "me": "you",
    "Me": "You",
}


def switch_persona_from_first_to_second_word(word: str):
    return forms.get(word, word)


def switch_persona_from_first_to_second_sentence(sentence: str):
    if not _has_nltk:
        raise ImportError("Cannot execute switching personas without nltk.")
    return " ".join(
        [
            switch_persona_from_first_to_second_word(word)
            for word in nltk.wordpunct_tokenize(sentence)  # type: ignore
        ]
    )


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


def create_text_to_tokenizer_chat(loaded_sample) -> str:
    return create_text_to_tokenizer(loaded_sample)


def create_text_to_tokenizer_one_step(loaded_sample, received_tokens: list[str]):
    sample = copy.deepcopy(loaded_sample)
    if len(received_tokens) > 0:
        received_tokens[0] = received_tokens[0].lstrip()
    sample["user_message"] = "".join(received_tokens)
    text_to_tokenizer = create_text_to_tokenizer(sample)
    return text_to_tokenizer


def retrieve_target_str(loaded_sample):
    return loaded_sample["candidates"][-1]


def create_system_traits(loaded_sample):
    system_traits = "You are a chatbot for the task where you try to impersonate a human who identifies himself with the following traits: "
    system_traits += " ".join(
        [
            switch_persona_from_first_to_second_sentence(sentence)
            for sentence in loaded_sample["personality"]
        ]
    )
    system_traits += " Your answers should be about a sentence long."
    return system_traits


def create_text_to_tokenizer_openai(loaded_sample, target: str | None = None) -> str:
    api_message = OpenAIMessage(
        system_message=create_system_traits(loaded_sample),
        messages=copy.deepcopy(loaded_sample["history"]),
        model="gpt-3.5-turbo-0613",
    )
    return api_message.construct_message()


def create_text_to_tokenizer_chat_openai(loaded_sample) -> str:
    history = copy.deepcopy(loaded_sample["history"])
    if len(loaded_sample["user_message"].strip()) != 0:
        history.append(copy.deepcopy(loaded_sample["user_message"]))

    api_message = OpenAIMessage(
        system_message=create_system_traits(loaded_sample),
        messages=history,
        model="gpt-3.5-turbo-0613",
    )
    return api_message.construct_message()


def create_app(
    dataset: "DatasetDict",
    generator_choices: dict[str, Generator],
    next_token_generator_choices: dict[str, Generator],
    get_persona_traits: Callable[[], list[str]],
):
    # create components
    visualize = Visualization(
        dataset=dataset,
        generator_choices=generator_choices,
    )
    generate = Generation(
        dataset=dataset,
        generator_choices=generator_choices,
        selectors={
            "do_sample": CheckBoxSelectorType(False),
            "top_p": MinMaxSelectorType(0, 1, default_value=1.0, step_size=0.05),
            "max_new_tokens": MinMaxSelectorType(10, 100, default_value=30),
            "num_return_sequences": MinMaxSelectorType(1, 20),
        },
        metrics_on_probs={"Perplexity": ProbsMetric("{:.5f}", False, Perplexity())},
        metrics_on_generated_text={
            "F1-Score": GeneratedTextMetric("{:.2%}", True, F1Score())
        },
    )

    chat = ChatComponent(
        title="chat",
        generator_choices=generator_choices,
        selectors={
            "do_sample": CheckBoxSelectorType(False),
            "top_p": MinMaxSelectorType(0, 1, default_value=1.0, step_size=0.05),
            "max_new_tokens": MinMaxSelectorType(10, 100, default_value=30),
            # "num_return_sequences": MinMaxSelectorType(1, 20),
            # TODO: right now regardless of num_return_sequences, only
            # one is displayed, add multiple sequences in chat component!
            "temperature": MinMaxSelectorType(0, 2, default_value=1.0, step_size=0.1),
        },
        get_persona_traits=get_persona_traits,
    )
    components: list[ComponentBase] = [generate, visualize, chat]
    if len(next_token_generator_choices) > 0:
        next_token = NextTokenPrediction(
            generator_choices=next_token_generator_choices, dataset=dataset
        )
        components.append(next_token)
    server = Server(__name__, components)
    return server.app
