from llm_generation_server.formatters.format import FormattedContext, Formatter
from typing import List, Callable
from dataclasses import dataclass
from heapq import nlargest
from llm_generation_server.server import Server


@dataclass
class Continuation:
    token: str
    prob: float


class SoftmaxFormatter(Formatter):
    def __init__(
        self,
        n_largest_tokens_to_return: int,
        endpoint_url: str,
        endpoint_callback: Callable,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.n_largest_tokens_to_return = n_largest_tokens_to_return
        self._possibilities = []
        self.endpoint_url = endpoint_url
        self.endpoint_callback = endpoint_callback

    @property
    def possibilities(self):
        return self._possibilities

    @possibilities.setter
    def possibilities(self, value):
        self.changed = True
        self._possibilities = value

    def assign_words_to_probs(self, probs: List[float], word_vocab: List[str]):
        n_largest = nlargest(
            self.n_largest_tokens_to_return, zip(probs, word_vocab), key=lambda x: x[0]
        )
        return [Continuation(x[1], x[0] * 100) for x in n_largest]

    def format(self):
        self.changed = False
        return FormattedContext(
            name=self.name,
            type="softmax",
            content=dict(possibilities=self.possibilities, address=self.endpoint_url),
        )

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])
