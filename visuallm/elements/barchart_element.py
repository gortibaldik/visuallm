from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Union

from flask import request

from visuallm.server import Server

from .element_base import ElementDescription, ElementWithEndpoint


@dataclass
class BarInfo:
    barTitle: str
    barHeights: List[float]
    barAnnotations: List[str]

    def __post_init__(self):
        for height in self.barHeights:
            if (height < 0) or (height > 100):
                raise ValueError(
                    f"Height should be between 0 and 100 (currently {height})"
                )


class BarChartElement(ElementWithEndpoint):
    def __init__(
        self,
        long_contexts: bool = False,
        names: List[str] = [],
        processing_callback: Optional[Callable[[], Any]] = None,
        name="barchart",
        **kwargs,
    ):
        """
        Args:
            `long_contexts` (bool, optional): If this flag is set, then the
                bar is displayed under the bar title, if it is not set, then the
                bar is displayed alongside the bar title. Defaults to False.
            `names` (List[str], optional): Names of the individual bars. These
                names are displayed above each individual bar if there are
                more than 1 bar or if `long_contexts` is set. There should be
                equal number of names to bar_heights. Defaults to [].
            `processing_callback` (Optional[Callable[[], None]): the callback
                function will be called just after the `BarChartElement`
                updated `self.selected,` so you can handle the change.
                Defaults to None, if `processing_callback == None` then no
                `Select` button will display on the frontend.
            `name` (str, optional): name of the element, doesn't have to be
                provided. Defaults to "barchart".
        """

        super().__init__(name=name, endpoint_callback=self.default_callback, **kwargs)

        self.processing_callback = processing_callback
        self._possibilities: List[BarInfo] = []
        self._selected: Optional[str] = None
        self.long_contexts = long_contexts
        self.names = names

    @property
    def possibilities(self) -> List[BarInfo]:
        return self._possibilities

    @possibilities.setter
    def possibilities(self, value: List[BarInfo]):
        self.changed = True
        self._possibilities = value

    @property
    def selected(self) -> str:
        assert self._selected is not None
        return self._selected

    @property
    def selectable(self):
        return self.processing_callback is not None

    def set_possibilities(
        self,
        bar_heights: Union[List[List[float]], Any],
        bar_annotations: List[List[str]],
        annotations: List[str],
    ):
        """
        Args:
            bar_heights (Union[List[List[float]], Any]): List of bar heights for each bar to be displayed.
                e.g. if the shape of list is len(bar_heigths) = N, and len(bar_heights[i]) = M for each i,
                then N lines each with M bars will be displayed.
            bar_annotations (List[List[str]]): List of bar annotations for each bar to be displayed.
                e.g. as in the previous example, bar_annotations[i][j] would be the text in
                j-th bar in i-th line
            annotations (List[str]): List of annotations for each group of bars to be displayed on
                single line.
        """
        self.possibilities = [
            BarInfo(annot, bar_height, bar_annot)
            for annot, bar_height, bar_annot in zip(
                annotations, bar_heights, bar_annotations
            )
        ]

    def check_possibilities_length(self):
        required_len = len(self.names)
        if required_len == 0:
            # if there isn't any name provided, then populate self.names
            # with number of empty strings equal to size of first barHeights
            if len(self.possibilities) != 0:
                required_len = len(self.possibilities[0].barHeights)
                self.names = ["" for _ in range(required_len)]
            else:
                self.names = []

        for p in self.possibilities:
            for arr, name in [
                (p.barHeights, "Bar Heights"),
                (p.barAnnotations, "Bar Annotations"),
            ]:
                if len(arr) != required_len:
                    raise ValueError(
                        f"{name}: {arr} ({len(arr)}), names: {self.names}"
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
                address=self.endpoint_url.removeprefix("/"),
                long_contexts=self.long_contexts,
                names=self.names,
                selectable=self.selectable,
            ),
        )

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])

    def default_callback(self):
        if not request.is_json:
            raise RuntimeError()

        # just for the type checker
        if request.json is None:
            raise RuntimeError()

        self._selected = request.json.get("selected")
        assert self.processing_callback is not None
        self.processing_callback()

        assert self.parent_component is not None
        return self.parent_component.fetch_info(fetch_all=False)
