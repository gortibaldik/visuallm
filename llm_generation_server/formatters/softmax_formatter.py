from dataclasses import dataclass
from heapq import nlargest
from typing import Any, Callable, List, Union

from llm_generation_server.formatters.format import FormattedContext, Formatter
from llm_generation_server.server import Server


@dataclass
class Continuation:
    content: str
    probs: List[List[float]]


class SoftmaxFormatter(Formatter):
    def __init__(
        self,
        n_largest_tokens_to_return: int,
        endpoint_url: str,
        endpoint_callback: Callable,
        long_contexts: bool = False,
        names: List[str] = [],
        selectable: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.n_largest_tokens_to_return = n_largest_tokens_to_return
        self._possibilities: List[Continuation] = []
        self.endpoint_url = endpoint_url
        self.endpoint_callback = endpoint_callback
        self.long_contexts = long_contexts
        self.names = names
        self.selectable = selectable

    @property
    def possibilities(self) -> List[Continuation]:
        return self._possibilities

    @possibilities.setter
    def possibilities(self, value: List[Continuation]):
        self.changed = True
        self._possibilities = value

    def assign_words_to_probs(
        self, probs: Union[List[List[float]], Any], word_vocab: List[str]
    ):
        n_largest = nlargest(
            self.n_largest_tokens_to_return,
            zip(*zip(*probs), word_vocab),
            key=lambda x: x[0],
        )
        return [Continuation(x[-1], list(x[0:-1])) for x in n_largest]

    def check_possibilities_length(self):
        required_len = len(self.names)
        for p in self.possibilities:
            if len(p.probs) != required_len:
                raise ValueError(
                    f"Probs: {p.probs} ({len(p.probs)}), names: {self.names}"
                    + f" ({len(self.names)})"
                )

    def format(self):
        self.changed = False
        self.check_possibilities_length()
        return FormattedContext(
            name=self.name,
            type="softmax",
            content=dict(
                possibilities=self.possibilities,
                address=self.endpoint_url,
                long_contexts=self.long_contexts,
                names=self.names,
                selectable=self.selectable,
            ),
        )

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])
