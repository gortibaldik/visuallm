import math
import random
from typing import List

from visuallm.component_base import ComponentBase
from visuallm.elements.barchart_element import BarChartElement


class BarChartComponentAdvanced(ComponentBase):
    def __init__(self):
        self.barchart_element = BarChartElement(
            long_contexts=True,
            names=["Quality", "Perplexity", "Consistency", "Fluency"],
        )
        self.init_barchart_element()
        super().__init__(
            name="advanced_barchart",
            title="Advanced BarChart",
            elements=[self.barchart_element],
        )

    def init_barchart_element(self):
        ds = []
        size_of_distro = 5
        for i in range(len(self.barchart_element.names)):
            ds.append(make_some_distribution(size_of_distro))

        # bar height is the height of the bar, should be between 0 and 100
        bar_heights = list(zip(*ds))

        # bar annotation is the text displayed within the bar
        bar_annotations = [[f"{h:.2f}" for h in hs] for hs in bar_heights]

        # annotation is the name of whole bar sub element
        annotations = [
            "Use the portable output format.",
            "Give very verbose output about all the program knows about.",
            "Terminate option list.",
            "You should document the library so that the potential user "
            + "could make sense of it.",
            "This will indicate the state of the repository that should be "
            + "evaluated.",
        ]
        self.barchart_element.set_possibilities(
            bar_heights, bar_annotations, annotations
        )


def make_some_distribution(size: int):
    d = random.choice(["uniform", "exponential"])

    if d == "uniform":
        return make_uniform_distribution(size)
    else:
        return make_exponential_distribution(size)


def make_uniform_distribution(size: int):
    return distributify([random.random() for _ in range(size)])


def make_exponential_distribution(size: int):
    return distributify([math.exp(random.random() * (i + 1)) for i in range(size)])


def distributify(d: List[float]):
    _sum = sum(d)
    return [c / _sum * 100 for c in d]
