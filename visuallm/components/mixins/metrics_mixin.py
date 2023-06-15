from typing import Any, Callable, Dict, List, Sequence, Tuple

from visuallm.elements.barchart_element import BarChartElement
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import ButtonElement, CheckBoxSubElement

GENERATED_TEXT_METRIC = Tuple[Callable[[str, str], Any], str, bool]
"""Args:
Callable: Metric which will be called to evaluate
str: Format of the value that should be displayed on the page, e.g.
    "{:.4f}" so that only 4 floating point numbers would be displayed
bool: Whether the bar is also scalable, or should be kept at 100 for the
    metric number to be better visible
"""

PROBS_METRIC = Tuple[Callable[[Any, Any], Any], str, bool]
"""Args:
Callable: Metric which will be called to evaluate
str: Format of the value that should be displayed on the page, e.g.
    "{:.4f}" so that only 4 floating point numbers would be displayed
bool: Whether the bar is also scalable, or should be kept at 100 for the
    metric number to be better visible
"""


class MetricsMixin:
    def __init__(
        self,
        on_metrics_change: Callable[[], None],
        metrics_on_generated_text: Dict[str, GENERATED_TEXT_METRIC] = {},
        metrics_on_probs: Dict[str, PROBS_METRIC] = {},
    ):
        self._select_metrics_heading = PlainTextElement(
            content="Which Metrics to Display", is_heading=True
        )
        self._select_metrics_elements: Dict[str, CheckBoxSubElement] = {}

        for dct in [metrics_on_generated_text, metrics_on_probs]:
            for key in dct:
                self._select_metrics_elements[key] = CheckBoxSubElement(key, True)
        self._ordering = list(metrics_on_generated_text.keys()) + list(
            metrics_on_probs.keys()
        )
        self._metrics_on_generated_text = metrics_on_generated_text
        self._metrics_on_probs = metrics_on_probs
        self._display_metrics_heading = PlainTextElement(
            content="Metrics on Generated Outputs", is_heading=True
        )
        self._display_metrics_element = BarChartElement(
            long_contexts=True, names=self._ordering
        )
        self._display_metrics_on_target_heading = PlainTextElement(
            content="Metrics on Target", is_heading=True
        )
        self._display_metrics_on_target_element = BarChartElement(
            long_contexts=True, names=self._ordering
        )

        self.metric_button_element = ButtonElement(
            subelements=list(self._select_metrics_elements.values()),
            button_text="Select Metrics to Display",
            processing_callback=self.metrics_processing_callback,
        )
        self._on_metrics_change = on_metrics_change

    @property
    def metrics_selection(self):
        return [self._select_metrics_heading, self.metric_button_element]

    @property
    def metrics_display(self):
        return [
            self._display_metrics_on_target_heading,
            self._display_metrics_on_target_element,
            self._display_metrics_heading,
            self._display_metrics_element,
        ]

    def _compute_metrics_for_element(
        self,
        generated_text_list: Sequence[str],
        label_text_list: Sequence[str],
        probs_encoded_list: Sequence[Any],
        generated_encoded_list: Sequence[Any],
        element: BarChartElement,
    ):
        bar_annotations: List[List[str]] = []
        bar_heights: List[List[float]] = []
        annotations: List[str] = []
        names: List[str] = []
        first_time: bool = True
        for (
            generated_text,
            label_text,
            labels_encoded,
            generated_encoded,
        ) in zip(
            generated_text_list,
            label_text_list,
            probs_encoded_list,
            generated_encoded_list,
        ):
            group_annotations: List[str] = []
            group_heights: List[float] = []
            for name in self._ordering:
                if not self._select_metrics_elements[name].selected:
                    continue
                if first_time:
                    names.append(name)

                if name in self._metrics_on_generated_text:
                    (
                        metric,
                        format_of_annotation,
                        scale_bar,
                    ) = self._metrics_on_generated_text[name]
                    result = metric(generated_text, label_text)
                else:
                    (
                        metric,
                        format_of_annotation,
                        scale_bar,
                    ) = self._metrics_on_probs[name]
                    result = metric(labels_encoded, generated_encoded)

                if scale_bar:
                    group_heights.append(min(result * 100, 100))
                else:
                    group_heights.append(100)
                group_annotations.append(format_of_annotation.format(result))

            first_time = False
            bar_annotations.append(group_annotations)
            bar_heights.append(group_heights)
            annotations.append(generated_text)

        element.set_possibilities(bar_heights, bar_annotations, annotations)
        element.names = names

    def compute_metrics_on_predicted(
        self,
        generated_text_list: Sequence[str],
        label_text_list: Sequence[str],
        probs_encoded_list: Sequence[Any],
        generated_encoded_list: Sequence[Any],
    ):
        self._compute_metrics_for_element(
            generated_text_list,
            label_text_list,
            probs_encoded_list,
            generated_encoded_list,
            self._display_metrics_element,
        )

    def compute_metrics_on_target(
        self,
        target: str,
        probs_target: Any,
        target_encoded: Any,
    ):
        self._compute_metrics_for_element(
            [target],
            [target],
            probs_target,
            target_encoded,
            self._display_metrics_on_target_element,
        )

    def metrics_processing_callback(self):
        self._on_metrics_change()
