import os

from datasets import DatasetDict, load_dataset
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from visuallm.components.generators.base import Generator
from visuallm.components.generators.huggingface import HuggingFaceGenerator
from visuallm.components.generators.openai import OpenAIGenerator

from .components.chat import get_persona_traits
from .create_app import (
    create_app,
    create_text_to_tokenizer,
    create_text_to_tokenizer_chat,
    create_text_to_tokenizer_chat_openai,
    create_text_to_tokenizer_one_step,
    create_text_to_tokenizer_openai,
    retrieve_target_str,
)

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
    create_text_to_tokenizer_chat=create_text_to_tokenizer_chat,
    create_text_to_tokenizer_one_step=create_text_to_tokenizer_one_step,
    retrieve_target_str=retrieve_target_str,
)
_generator_choices["gpt2"] = generator

if "OPENAI_API_KEY" in os.environ:
    open_ai_generator = OpenAIGenerator(
        create_text_to_tokenizer=create_text_to_tokenizer_openai,
        create_text_to_tokenizer_chat=create_text_to_tokenizer_chat_openai,
        retrieve_target_str=retrieve_target_str,
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
