from datasets import DatasetDict, load_dataset
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from visuallm.components.GenerationComponent import GeneratedTextMetric, ProbsMetric
from visuallm.components.mixins.generation_selectors_mixin import (
    CheckBoxSelectorType,
    MinMaxSelectorType,
)
from visuallm.server import Server

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

# create components
visualize = Visualization(dataset=dataset)
generate = Generation(
    dataset=dataset,
    model=model,
    tokenizer=tokenizer,  # type: ignore
    selectors={
        "do_sample": CheckBoxSelectorType(False),
        "top_k": MinMaxSelectorType(0, 1000),
        "max_new_tokens": MinMaxSelectorType(10, 100, default_value=30),
        "num_return_sequences": MinMaxSelectorType(1, 20),
    },
    metrics_on_probs={"Perplexity": ProbsMetric("{:.5f}", False, Perplexity())},
    metrics_on_generated_text={
        "F1-Score": GeneratedTextMetric("{:.2%}", True, F1Score())
    },
)
next_token = NextTokenPrediction(
    model=model, tokenizer=tokenizer, dataset=dataset, n_largest_tokens_to_return=8
)
server = Server(__name__, [visualize, generate, next_token])
app = server.app
