import copy
from typing import List, Optional

from datasets import DatasetDict, load_dataset
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from visuallm.components.GenerationComponent import GeneratedTextMetric, ProbsMetric
from visuallm.components.mixins.generation_selectors_mixin import (
    CheckBoxSelectorType,
    MinMaxSelectorType,
)
from visuallm.components.mixins.Generator import (
    HuggingFaceGenerator,
    OpenAIGenerator,
    switch_persona_from_first_to_second_sentence,
)
from visuallm.server import Server

from .components.chat import ChatComponent
from .components.generation import Generation
from .components.metrics import F1Score, Perplexity
from .components.next_token_prediction import NextTokenPrediction
from .components.visualization import Visualization

# load models
dataset = load_dataset("bavard/personachat_truecased")
if not isinstance(dataset, DatasetDict):
    raise ValueError("Only dataset and dataset dict are supported")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")


def create_text_to_tokenizer(loaded_sample, target: Optional[str] = None) -> str:
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


def create_text_to_tokenizer_one_step(loaded_sample, received_tokens: List[str]):
    sample = copy.deepcopy(loaded_sample)
    if len(received_tokens) > 0:
        received_tokens[0] = received_tokens[0].lstrip()
    sample["user_message"] = "".join(received_tokens)
    text_to_tokenizer = create_text_to_tokenizer(sample)
    return text_to_tokenizer


def retrieve_target_str(loaded_sample):
    return loaded_sample["candidates"][-1]


def create_text_to_tokenizer_openai(loaded_sample, target: Optional[str] = None):
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

    return {"model": model, "messages": messages}


generator = HuggingFaceGenerator(
    model=model,
    tokenizer=tokenizer,
    create_text_to_tokenizer=create_text_to_tokenizer,
    create_text_to_tokenizer_one_step=create_text_to_tokenizer_one_step,
    retrieve_target_str=retrieve_target_str,
)

open_ai_generator = OpenAIGenerator(
    create_text_to_tokenizer_openai, retrieve_target_str=retrieve_target_str
)

# create components
visualize = Visualization(
    dataset=dataset,
    generator_choices={"gpt-3.5-turbo-0613": open_ai_generator, "gpt2": generator},
)
generate = Generation(
    dataset=dataset,
    generator_choices={"gpt-3.5-turbo-0613": open_ai_generator, "gpt2": generator},
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
    generator_choices={"gpt-3.5-turbo-0613": open_ai_generator, "gpt2": generator},
    selectors={
        "do_sample": CheckBoxSelectorType(False),
        "top_p": MinMaxSelectorType(0, 1, default_value=1.0, step_size=0.05),
        "max_new_tokens": MinMaxSelectorType(10, 100, default_value=30),
        "num_return_sequences": MinMaxSelectorType(1, 20),
        "temperature": MinMaxSelectorType(0, 2, default_value=1.0, step_size=0.1),
    },
)
next_token = NextTokenPrediction(generator=generator, dataset=dataset)
server = Server(__name__, [generate, next_token, visualize, chat])
app = server.app
