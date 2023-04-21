import random

import numpy as np
import requests
from flask import jsonify, request

from llm_generation_server.component_base import ComponentBase
from llm_generation_server.formatters.plain_formatter import PlainFormatter
from llm_generation_server.formatters.sample_selector_formatter import (
    MinMaxSelectorFormatter,
)
from llm_generation_server.formatters.softmax_formatter import SoftmaxFormatter
from llm_generation_server.formatters.table_formatter import TableFormatter


class ExampleNextTokenPredictionComponent(ComponentBase):
    def __init__(self):
        self.main_heading_formatter = PlainFormatter(
            name="main_heading",
            is_heading=True,
            heading_level=2,
            content="Next Token Prediction",
        )
        self.generated_formatter = PlainFormatter(name="generated")
        self.generated_heading_formatter = PlainFormatter(
            name="generated_heading", content="Generated Context: ", is_heading=True
        )
        self.initial_context_formatter = TableFormatter(name="initial_context")
        self.softmax_heading_formatter = PlainFormatter(
            name="softmax_heading", content="Possible continuations: ", is_heading=True
        )
        self.softmax_formatter = SoftmaxFormatter(
            name="softmax",
            n_largest_tokens_to_return=10,
            endpoint_url="/select_next_token",
            endpoint_callback=self.select_next_token,
            names=["Estimated Probability"],
            selectable=True,
        )
        self.sample_selector_formatter = MinMaxSelectorFormatter(
            name="sample_selector",
            sample_min=0,
            sample_max=10,
            endpoint_callback=self.select_sample,
            endpoint_url="/select_sample",
        )
        super().__init__(
            default_url="/fetch_next_token",
            default_callback=self.initial_fetch,
            name="next_token_prediction",
            title="Next Token Prediction",
            formatters=[
                self.main_heading_formatter,
                self.sample_selector_formatter,
                self.initial_context_formatter,
                self.generated_heading_formatter,
                self.generated_formatter,
                self.softmax_heading_formatter,
                self.softmax_formatter,
            ],
        )

        self.load_dataset_sample(0)

    def initialize_vocab(self):
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        self.word_vocab = [x.decode("utf-8") for x in response.content.splitlines()]
        self.ix_arr = list(range(len(self.word_vocab)))

    def initial_fetch(self, fetch_all=True):
        probs = self.get_next_token_predictions()
        words = self.softmax_formatter.assign_words_to_probs(probs, self.word_vocab)
        self.softmax_formatter.possibilities = words

        return super().fetch_info(fetch_all=fetch_all)

    def select_sample(self):
        if not request.is_json:
            return jsonify(dict(result="failure"))
        sample_n: int = request.get_json().get("sample_n")
        self.load_dataset_sample(sample_n)
        return self.initial_fetch(fetch_all=False)

    def select_next_token(self):
        if not request.is_json:
            return jsonify(dict(result="failure"))
        token: str = request.get_json().get("token")
        self.generated_formatter.content += f" {token}"
        return self.initial_fetch(fetch_all=False)

    def load_dataset_sample(self, sample_n: int):
        headers = ["No.", "Turn"]
        rows = [
            [i, x]
            for i, x in enumerate(
                [
                    f"{sample_n}: This is first row",
                    f"{sample_n}: This is second row",
                    f"{sample_n}: This is third row",
                    f"{sample_n}: This is fourth row",
                    f"{sample_n}: This is fifth row",
                ]
            )
        ]
        self.initial_context_formatter.clear()
        self.initial_context_formatter.add_table("Longer Context", headers, rows)
        self.generated_formatter.content = ""

        for j in range(len(rows) - 1, 0, -1):
            for i in range(j):
                self.initial_context_formatter.add_connection(
                    "Longer Context", j, "Longer Context", i, 3, "nn"
                )

    def get_next_token_predictions(self):
        n = self.softmax_formatter.n_largest_tokens_to_return
        K = n * 3
        twenty_ixes = random.choices(self.ix_arr, k=K)
        twenty_probs = [random.random() for _ in range(K)]
        twenty_probs = np.exp(twenty_probs)
        twenty_probs /= np.sum(twenty_probs)
        probs = np.zeros((len(self.word_vocab), 1))
        probs[twenty_ixes, 0] = twenty_probs * 100
        return probs
