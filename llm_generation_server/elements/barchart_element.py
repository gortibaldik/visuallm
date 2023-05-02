from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Union

from flask import request

from llm_generation_server.server import Server

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
        selectable: bool = True,
        name="barchart",
        endpoint_callback: Optional[Callable] = None,
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
            `selectable` (bool, optional): If this flag is set, then there is
                an input radio selector displayed near each bar and a select
                button is displayed under the bar display. Defaults to True.
            `name` (str, optional): name of the element, doesn't have to be
                provided. Defaults to "barchart".
            `endpoint_callback`: the callback function that will be called when
                the user clicks the button on the frontend. Defaults to False.
                False means that empty function will be used as a callback.
        """
        if endpoint_callback is None:
            endpoint_callback = self.default_callback

        super().__init__(name=name, endpoint_callback=endpoint_callback, **kwargs)

        self._possibilities: List[BarInfo] = []
        self._selected: Optional[str] = None
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

    @property
    def selected(self) -> str:
        if self._selected is None:
            raise ValueError()
        return self._selected

    def set_possibilities(
        self,
        bar_heights: Union[List[List[float]], Any],
        bar_annotations: List[List[str]],
        annotations: List[str],
    ):
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
            required_len = len(self.possibilities[0].barHeights)
            self.names = ["" for _ in range(required_len)]

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

    def default_callback(self, return_response=True):
        if return_response:
            return dict(result="success")

        if not request.is_json:
            raise RuntimeError()

        # just for the type checker
        if request.json is None:
            raise RuntimeError()

        self._selected = request.json.get("selected")
