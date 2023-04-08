from llm_generation_server.formatters.format import FormattedContext
from typing import List
from dataclasses import dataclass
from heapq import nlargest
from llm_generation_server.formatters.format import FormattedContext

@dataclass
class Continuation:
    token: str
    prob: float

class SoftmaxFormatter:
    def __init__(self, n_largest_tokens_to_return: int):
        self.n_largest_tokens_to_return = n_largest_tokens_to_return
        self.possibilities = []

    def assign_words_to_probs(self, probs: List[float], word_vocab: List[str]):
        n_largest = nlargest(
            self.n_largest_tokens_to_return,
            zip(probs, word_vocab),
            key=lambda x: x[0]
        )
        return [Continuation(x[1], x[0] * 100) for x in n_largest]

    def format(self):
        return FormattedContext(
            type="softmax",
            content=self.possibilities
        )