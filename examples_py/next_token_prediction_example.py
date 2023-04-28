import random
from heapq import nlargest

import numpy as np
import requests
from flask import jsonify, request

from llm_generation_server.component_base import ComponentBase
from llm_generation_server.elements.barchart_element import BarChartElement
from llm_generation_server.elements.plain_text_element import PlainTextElement
from llm_generation_server.elements.selector_element import (
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
    SelectorElement,
)
from llm_generation_server.elements.table_element import TableElement


class ExampleNextTokenPredictionComponent(ComponentBase):
    def __init__(self):
        self.main_heading_element = PlainTextElement(
            is_heading=True,
            heading_level=2,
            content="Next Token Prediction",
        )
        self.generated_element = PlainTextElement()
        self.generated_heading_element = PlainTextElement(
            content="Generated Context: ", is_heading=True
        )
        self.initial_context_element = TableElement()
        self.softmax_heading_element = PlainTextElement(
            content="Possible continuations: ", is_heading=True
        )
        self._n_largest_tokens_to_return = 10
        self.softmax_element = BarChartElement(
            endpoint_callback=self.select_next_token,
            names=["Estimated Probability"],
            selectable=True,
        )
        self.sample_selector_element = MinMaxSubElement(
            text="Select sample:",
            sample_min=0,
            sample_max=10_000_000,
        )
        self.model_selector = ChoicesSubElement(
            text="Select model:", choices=["first", "second", "third"]
        )
        self.check_box_selector = CheckBoxSubElement(text="Use Sampling:")
        self.selector_element = SelectorElement(
            button_text="Send Configuration to Server",
            endpoint_callback=self.select_sample,
            subelements=[
                self.sample_selector_element,
                self.model_selector,
                self.check_box_selector,
            ],
        )

        super().__init__(
            default_callback=self.initial_fetch,
            name="next_token_prediction",
            title="Next Token Prediction",
            elements=[
                self.main_heading_element,
                self.selector_element,
                self.initial_context_element,
                self.generated_heading_element,
                self.generated_element,
                self.softmax_heading_element,
                self.softmax_element,
            ],
        )

        self._initialize_vocab()
        self.load_dataset_sample()

    def _initialize_vocab(self):
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        self.word_vocab = [x.decode("utf-8") for x in response.content.splitlines()]
        self.ix_arr = list(range(len(self.word_vocab)))

    def initial_fetch(self, fetch_all=True):
        probs = self.get_next_token_predictions()
        n_largest_probs = nlargest(
            self._n_largest_tokens_to_return,
            zip(*zip(*probs), self.word_vocab),
            key=lambda x: x[0],
        )
        bar_heights = [x[:-1] for x in n_largest_probs]
        bar_annotations = [[f"{x[0] :.2f}%"] for x in n_largest_probs]
        annotations = [x[-1] for x in n_largest_probs]
        self.softmax_element.set_possibilities(
            bar_heights, bar_annotations, annotations
        )

        return super().fetch_info(fetch_all=fetch_all)

    def select_sample(self):
        self.selector_element.default_select_callback()
        self.load_dataset_sample()
        return self.initial_fetch(fetch_all=False)

    def select_next_token(self):
        if not request.is_json:
            return jsonify(dict(result="failure"))
        token: str = request.get_json().get("token")
        self.generated_element.content += f" {token}"
        return self.initial_fetch(fetch_all=False)

    def load_dataset_sample(self):
        sample_n = self.sample_selector_element.selected
        model = self.model_selector.selected
        sampling = self.check_box_selector.selected
        print(sample_n, model)
        headers = ["No.", "Turn"]
        rows = [
            [i, x]
            for i, x in enumerate(
                [
                    f"[{model}] {sample_n}: This is first row (sampling: {sampling})",
                    f"[{model}] {sample_n}: This is second row (sampling: {sampling})",
                    f"[{model}] {sample_n}: This is third row (sampling: {sampling})",
                    f"[{model}] {sample_n}: This is fourth row (sampling: {sampling})",
                    f"[{model}] {sample_n}: This is fifth row (sampling: {sampling})",
                ]
            )
        ]
        self.initial_context_element.clear()
        self.initial_context_element.add_table("Longer Context", headers, rows)
        self.generated_element.content = ""

        for j in range(len(rows) - 1, 0, -1):
            for i in range(j):
                self.initial_context_element.add_link_between_rows(
                    "Longer Context", j, "Longer Context", i, 3, "nn"
                )

    def get_next_token_predictions(self):
        n = self._n_largest_tokens_to_return
        K = n * 3
        twenty_ixes = random.choices(self.ix_arr, k=K)
        twenty_probs = [random.random() for _ in range(K)]
        twenty_probs = np.exp(twenty_probs)
        twenty_probs /= np.sum(twenty_probs)
        probs = np.zeros((len(self.word_vocab), 1))
        probs[twenty_ixes, 0] = twenty_probs * 100
        return probs
