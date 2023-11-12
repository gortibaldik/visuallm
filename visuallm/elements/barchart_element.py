from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from flask import request

from .element_base import ElementWithEndpoint


@dataclass
class PieceInfo:

    """BarChart element is composed of pieces. Each piece contains multiple bars, which
    display some information. This class describes one piece, with the title,
    all the bars, bar annotations and names above the bars that should be displayed.

    Args:
    ----
        pieceTitle (str): Title displayed at the top place of the piece
        barHeights (str): Heights of the individual bars in the piece, should be
            between 0 and 100
        barAnnotations (str): Annotations displayed inside the individual bars in the
            piece.
        barNames (List[str]): Names displayed above the individual bars in the piece
    """

    pieceTitle: str
    """Title displayed at the top place of the piece"""
    barHeights: list[float]
    """Heights of the individual bars in the piece, should be
    between 0 and 100"""
    barAnnotations: list[str]
    """Annotations displayed inside the individual bars in the
    piece."""
    barNames: list[str]
    """Names displayed above the individual bars in the piece"""

    def __post_init__(self):
        for height in self.barHeights:
            if (height < 0) or (height > 100):
                raise ValueError(
                    f"Height should be between 0 and 100 (currently {height})"
                )
        l1, l2, l3 = len(self.barHeights), len(self.barAnnotations), len(self.barNames)

        if l1 != l2 or l2 != l3:
            raise ValueError(
                "All three of barHeights, barAnnotations and barNames should"
                f"be of the same length: {l1}, {l2}, {l3}"
            )


class BarChartElement(ElementWithEndpoint):
    def __init__(
        self,
        long_contexts: bool = False,
        processing_callback: Callable[[], Any] | None = None,
        name="barchart",
        endpoint_url: str | None = None,
    ):
        """Initialize BarChart Element. This element serves to display metrics and can have 2
        major use-cases:
        1. selectable: processing callback is set to some function and allows the user to
            select some value according to metrics
        2. non-selectable: just display the metrics

        Args:
        ----
            long_contexts (bool, optional): If this flag is set, then the
                bars are displayed under the piece title, if it is not set, then the
                bar is displayed alongside the piece title. Defaults to False.
            processing_callback (Optional[Callable[[], None]): the callback
                function will be called just after the `BarChartElement`
                updated `self.selected,` so you can handle the change.
                Defaults to None, if `processing_callback == None` then no
                `Select` button will display on the frontend.
            name (str, optional): name of the element, doesn't have to be
                provided. Defaults to "barchart".
            endpoint_url (str): url of the endpoint for the call made by pressing the
                barchart button
        """
        super().__init__(name=name, type="softmax", endpoint_url=endpoint_url)

        self.processing_callback = processing_callback
        self._piece_infos: list[PieceInfo] = []
        self._selected: str | None = None
        self.long_contexts = long_contexts

    @property
    def selected(self) -> str:
        """Return the last value that the user selected in the frontend for the barchart element."""
        if not self.selectable:
            raise ValueError(
                "The BarChart element isn't in the configuration where user can select anything "
                "in the frontend (self.processing_callback is None) hence the `selected` prop "
                "is undefined!"
            )
        if self._selected is None:
            raise RuntimeError("selected wasn't populated yet!")
        return self._selected

    @property
    def selectable(self):
        """Whether the user can select a value in the frontend of this element."""
        return self.processing_callback is not None

    @property
    def piece_infos(self) -> list[PieceInfo]:
        return self._piece_infos

    def set_piece_infos(self, piece_infos: list[PieceInfo]):
        # changed is a property that is checked to include every change
        # in the message from BE to FE, essential for the app to function
        self.set_changed()
        self._piece_infos = piece_infos

    def construct_element_configuration(self):
        return {
            "piece_infos": self.piece_infos,
            "long_contexts": self.long_contexts,
            "selectable": self.selectable,
        }

    def endpoint_callback(self):
        """Populate self.selected and sets
        self.changed so that the user can find out that
        the value of this element was changed from the frontend.

        Isn't used at all if the processing callback isn't provided.
        """
        if not request.is_json:
            raise RuntimeError()

        # just for the type checker
        if request.json is None:
            raise RuntimeError()

        # changed is simply set to True as we do not have any means of testing whether
        # the user simply didn't selected the same value multiple times
        self.set_changed()
        self._selected = request.json.get("selected")
        if self.processing_callback is None:
            raise RuntimeError(
                "Cannot call endpoint_callback on an element without `self.processing_callback()`"
            )
        self.processing_callback()

        if self.parent_component is None:
            raise RuntimeError(
                "Cannot call endpoint_callback on an element not registered to any component!"
            )
        return self.parent_component.fetch_info(fetch_all=False)
