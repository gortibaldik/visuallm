import math
import random

from visuallm.component_base import ComponentBase
from visuallm.elements.barchart_element import BarChartElement, PieceInfo


class BarChartComponentAdvanced(ComponentBase):
    def __init__(self):
        super().__init__(name="advanced_barchart", title="Advanced BarChart")
        self._names_of_bars = ["Quality", "Perplexity", "Consistency", "Fluency"]
        self.barchart_element = BarChartElement(long_contexts=True)
        self.add_element(self.barchart_element)
        self.init_barchart_element()

    def init_barchart_element(self) -> None:
        distributions: list[list[float]] = []
        size_of_distro = 5
        for _ in range(len(self._names_of_bars)):
            distributions.append(make_some_distribution(size_of_distro))

        # names of the whole piece with multiple bars
        piece_names = [
            "Use the portable output format.",
            "Give very verbose output about all the program knows about.",
            "Terminate option list.",
            "You should document the library so that the potential user "
            "could make sense of it.",
            "This will indicate the state of the repository that should be "
            "evaluated.",
        ]

        piece_infos: list[PieceInfo] = []
        for i in range(size_of_distro):
            # heights of individual bars in the piece
            bar_heights = [distro[i] for distro in distributions]

            # annotations inside individual bars in the piece
            bar_annotations = [f"{h:.2f}" for h in bar_heights]
            piece_infos.append(
                PieceInfo(
                    pieceTitle=piece_names[i],
                    barHeights=bar_heights,
                    barAnnotations=bar_annotations,
                    barNames=self._names_of_bars,
                )
            )

        self.barchart_element.set_piece_infos(piece_infos)


def make_some_distribution(size: int):
    d = random.choice(["uniform", "exponential"])  # noqa: S311

    if d == "uniform":
        return make_uniform_distribution(size)
    else:
        return make_exponential_distribution(size)


def make_uniform_distribution(size: int):
    return distributify([random.random() for _ in range(size)])  # noqa: S311


def make_exponential_distribution(size: int):
    return distributify(
        [math.exp(random.random() * (i + 1)) for i in range(size)]  # noqa: S311
    )


def distributify(d: list[float]):
    _sum = sum(d)
    return [c / _sum * 100 for c in d]
