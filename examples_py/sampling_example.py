import math
import random

from llm_generation_server.component_base import ComponentBase
from llm_generation_server.elements.barchart_element import BarChartElement
from llm_generation_server.elements.plain_text_element import PlainTextElement
from llm_generation_server.elements.selector_element import (
    MinMaxSubElement,
    SelectorElement,
)


class ExampleSamplingComponent(ComponentBase):
    def __init__(self):
        self.main_heading_element = PlainTextElement(
            name="main_heading", is_heading=True, heading_level=2, content="Sampling"
        )
        self.sample_selector_element = MinMaxSubElement(
            sample_min=-5, sample_max=5, text="Select Sample:"
        )
        self.selector_element = SelectorElement(
            button_text="Select Sample",
            subelements=[self.sample_selector_element],
            endpoint_callback=self.select_sample,
        )
        self.softmax_element = BarChartElement(
            endpoint_callback=lambda: ...,
            long_contexts=True,
            names=["SuperProb", "ExtraProb", "FantasticProb"],
            selectable=False,
        )
        self.load_dataset_sample()

        super().__init__(
            name="sampling",
            title="Sampling",
            elements=[
                self.main_heading_element,
                self.selector_element,
                self.softmax_element,
            ],
        )

    def load_dataset_sample(self):
        sample_n = self.sample_selector_element.selected
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
        self.softmax_element.set_possibilities(probs, rows)

    def select_sample(self):
        self.selector_element.default_select_callback()
        self.load_dataset_sample()
        return self.fetch_info(fetch_all=False)
