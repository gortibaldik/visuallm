import math
import random

from flask import jsonify, request

from llm_generation_server.component_base import ComponentBase
from llm_generation_server.formatters.plain_formatter import PlainFormatter
from llm_generation_server.formatters.sample_selector_formatter import (
    MinMaxSelectorFormatter,
)
from llm_generation_server.formatters.softmax_formatter import SoftmaxFormatter


class ExampleSamplingComponent(ComponentBase):
    def __init__(self):
        self.main_heading_formatter = PlainFormatter(
            name="main_heading", is_heading=True, heading_level=2, content="Sampling"
        )
        self.sample_selector_formatter = MinMaxSelectorFormatter(
            name="sample_selector",
            sample_min=0,
            sample_max=10,
            endpoint_callback=self.select_sample,
            endpoint_url="/select_sample_sampling",
        )
        self.softmax_formatter = SoftmaxFormatter(
            name="softmax",
            n_largest_tokens_to_return=10,
            endpoint_url="/select_samples",
            endpoint_callback=lambda: ...,
            long_contexts=True,
            names=["SuperProb", "ExtraProb", "FantasticProb"],
            selectable=False,
        )
        self.load_dataset_sample(0)

        super().__init__(
            default_url="/fetch_sampling",
            name="sampling",
            title="Sampling",
            formatters=[
                self.main_heading_formatter,
                self.sample_selector_formatter,
                self.softmax_formatter,
            ],
        )

    def load_dataset_sample(self, sample_n: int):
        rows = [
            x
            for x in [
                f"{sample_n}: This is first row",
                f"{sample_n}: This is second row",
                f"{sample_n}: This is third row",
                f"{sample_n}: This is fourth row",
                f"{sample_n}: This is fifth row",
            ]
        ]

        def make_distribution(lst):
            lst_sum = sum(lst)
            return [c / lst_sum * 100 for c in lst]

        yet_other_probs = make_distribution(
            [random.random() for i, _ in enumerate(rows)]
        )
        other_probs = make_distribution([math.exp(i) for i, _ in enumerate(rows)])
        probs = [
            [i * 10 + 10, o1, o2]
            for i, (o1, o2) in enumerate(zip(other_probs, yet_other_probs))
        ]
        words = self.softmax_formatter.assign_words_to_probs(probs, rows)
        self.softmax_formatter.possibilities = words

    def select_sample(self):
        if not request.is_json:
            return jsonify(dict(result="failure"))
        sample_n: int = request.get_json().get("sample_n")
        self.load_dataset_sample(sample_n)
        return self.fetch_info(fetch_all=False)
