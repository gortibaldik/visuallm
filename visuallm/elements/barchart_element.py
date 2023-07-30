from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from flask import request

from .element_base import ElementWithEndpoint


@dataclass
class PieceInfo:
    """
    BarChart element is composed of pieces. Each piece contains multiple bars, which
    display some information. This class describes one piece, with the title,
    all the bars, bar annotations and names above the bars that should be displayed.

    Args:
        pieceTitle (str): Title displayed at the top place of the piece
        barHeights (str): Heights of the individual bars in the piece, should be
            between 0 and 100
        barAnnotations (str): Annotations displayed inside the individual bars in the
            piece.
        barNames (List[str]): Names displayed above the individual bars in the piece
    """

    pieceTitle: str
    """Title displayed at the top place of the piece"""
    barHeights: List[float]
    """Heights of the individual bars in the piece, should be
    between 0 and 100"""
    barAnnotations: List[str]
    """Annotations displayed inside the individual bars in the
    piece."""
    barNames: List[str]
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
        processing_callback: Optional[Callable[[], Any]] = None,
        name="barchart",
        **kwargs,
    ):
        """
        Args:
            `long_contexts` (bool, optional): If this flag is set, then the
                bars are displayed under the piece title, if it is not set, then the
                bar is displayed alongside the piece title. Defaults to False.
            `processing_callback` (Optional[Callable[[], None]): the callback
                function will be called just after the `BarChartElement`
                updated `self.selected,` so you can handle the change.
                Defaults to None, if `processing_callback == None` then no
                `Select` button will display on the frontend.
            `name` (str, optional): name of the element, doesn't have to be
                provided. Defaults to "barchart".
        """

        super().__init__(name=name, type="softmax", **kwargs)

        self.processing_callback = processing_callback
        self._piece_infos: List[PieceInfo] = []
        self._selected: Optional[str] = None
        self.long_contexts = long_contexts

    @property
    def selected(self) -> str:
        assert self._selected is not None
        return self._selected

    @property
    def selectable(self):
        return self.processing_callback is not None

    @property
    def piece_infos(self) -> List[PieceInfo]:
        self.changed = True
        return self._piece_infos

    def set_piece_infos(self, piece_infos: List[PieceInfo]):
        """ """
        self._piece_infos = piece_infos

    def construct_element_configuration(self):
        return dict(
            piece_infos=self.piece_infos,
            long_contexts=self.long_contexts,
            selectable=self.selectable,
        )

    def endpoint_callback(self):
        """This callback populates self.selected and sets
        self.changed so that the user can find out that
        the value of this element was changed from the frontend.

        Isn't used at all if the processing callback isn't provided.
        """
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
