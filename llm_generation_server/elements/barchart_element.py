from dataclasses import dataclass
from heapq import nlargest
from typing import Any, List, Union

from llm_generation_server.server import Server

from .element_base import ElementDescription, ElementWithEndpoint


@dataclass
class BarInfo:
    barTitle: str
    barHeights: List[List[float]]


class BarChartElement(ElementWithEndpoint):
    def __init__(
        self,
        n_largest_tokens_to_return: int,
        long_contexts: bool = False,
        names: List[str] = [],
        selectable: bool = True,
        name="barchart",
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.n_largest_tokens_to_return = n_largest_tokens_to_return
        self._possibilities: List[BarInfo] = []
        self.long_contexts = long_contexts
        self.names = names
        self.selectable = selectable

    @property
    def possibilities(self) -> List[BarInfo]:
        return self._possibilities

    @possibilities.setter
    def possibilities(self, value: List[BarInfo]):
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
        return [BarInfo(x[-1], list(x[0:-1])) for x in n_largest]

    def check_possibilities_length(self):
        required_len = len(self.names)
        for p in self.possibilities:
            if len(p.barHeights) != required_len:
                raise ValueError(
                    f"Probs: {p.barHeights} ({len(p.barHeights)}), names: {self.names}"
                    + f" ({len(self.names)})"
                )

    def construct_element_description(self):
        self.changed = False
        self.check_possibilities_length()
        return ElementDescription(
            name=self.name,
            type="softmax",
            configuration=dict(
                bar_infos=self.possibilities,
                address=self.endpoint_url,
                long_contexts=self.long_contexts,
                names=self.names,
                selectable=self.selectable,
            ),
        )

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])
