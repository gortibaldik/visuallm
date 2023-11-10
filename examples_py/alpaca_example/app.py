from datasets import DatasetDict, load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from visuallm.components.generators.huggingface import HuggingFaceGenerator

from .create_app import create_app

dataset = load_dataset("yahma/alpaca-cleaned")
if not isinstance(dataset, DatasetDict):
    raise TypeError("Only dataset dict is supported now")

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")


def create_text_to_tokenizer(loaded_sample, target: str | None = None) -> str:
    text_to_tokenizer = f"Instruction: {loaded_sample['instruction']} Answer:"
    if target is not None:
        text_to_tokenizer += " " + target
    return text_to_tokenizer


def create_text_to_tokenizer_one_step(loaded_sample, received_tokens: list[str]) -> str:
    # one step prediction means that the model is used to predict tokens one per one
    # received_tokens list contains already selected tokens

    text_to_tokenizer = (
        f"Instruction: {loaded_sample['instruction']} Answer:"
        + "".join(received_tokens)
    )
    return text_to_tokenizer


def retrieve_target_str(loaded_sample):
    return loaded_sample["output"]


generator = HuggingFaceGenerator(
    model=model,
    tokenizer=tokenizer,
    create_text_to_tokenizer=create_text_to_tokenizer,
    create_text_to_tokenizer_one_step=create_text_to_tokenizer_one_step,
    retrieve_target_str=retrieve_target_str,
)

app = create_app(dataset=dataset, generator_choices={"gpt2": generator})
