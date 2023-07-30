from datasets import load_dataset
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from visuallm.components.GenerationComponent import ProbsMetric
from visuallm.components.mixins.generation_selectors_mixin import (
    CheckBoxSelectorType,
    MinMaxSelectorType,
)
from visuallm.server import Server

from .components.generation import Generation
from .components.metrics import Perplexity
from .components.next_token_prediction import NTP
from .components.visualization import Visualization

# load models
dataset = load_dataset("bavard/personachat_truecased")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

# create components
vis = Visualization(dataset=dataset)
gen = Generation(
    dataset=dataset,
    model=model,
    tokenizer=tokenizer,
    selectors={
        "do_sample": CheckBoxSelectorType(False),
        "top_k": MinMaxSelectorType(0, 1000),
        "max_new_tokens": MinMaxSelectorType(10, 100, default_value=30),
        "num_return_sequences": MinMaxSelectorType(1, 20),
    },
    metrics_on_probs={"Perplexity": ProbsMetric("{:.5f}", False, Perplexity())},
)
ntp = NTP(model=model, tokenizer=tokenizer, dataset=dataset)
server = Server(__name__, [vis, gen, ntp])
app = server.app
