from components.generation import Generation
from components.metrics import Perplexity
from components.next_token_prediction import NTP
from components.visualization import Visualization
from datasets import load_dataset
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer

from visuallm.server import Server

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
    selectors={"do_sample": False, "top_k": (0, 1000), "max_new_tokens": (10, 100, 30)},
    metrics_on_probs={"Perplexity": (Perplexity(), "{:5f}", False)},
)
ntp = NTP(model=model, tokenizer=tokenizer, dataset=dataset)
server = Server(__name__, [vis, gen, ntp])
app = server.app
