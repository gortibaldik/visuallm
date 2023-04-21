from llm_generation_server.formatters.format import FormattedContext, Formatter
from llm_generation_server.server import Server
from typing import Callable, List


class SampleSelectorFormatter(Formatter):
    def __init__(self, endpoint_url: str, endpoint_callback: Callable, **kwargs):
        super().__init__(**kwargs)
        self.subtype = "invalid"
        self.type = "sample_selector"
        self.other_args = {}
        self.endpoint_url = endpoint_url
        self.endpoint_callback = endpoint_callback

    def format(self):
        self.changed = False
        return FormattedContext(
            name=self.name,
            type=self.type,
            content=dict(
                subtype=self.subtype, **self.other_args, address=self.endpoint_url
            ),
        )

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])


class MinMaxSelectorFormatter(SampleSelectorFormatter):
    def __init__(self, sample_min: int, sample_max: int, **kwargs):
        super().__init__(**kwargs)
        if sample_min >= sample_max:
            raise ValueError(
                f"sample_min ({sample_min}) should be bigger than sample_max "
                + f"({sample_max})"
            )
        self.other_args = dict(min=sample_min, max=sample_max, selected=sample_min)
        self.subtype = "min_max"

    @property
    def selected(self):
        return self.other_args["selected"]

    @selected.setter
    def selected(self, value):
        if (value > self.other_args["max"]) or (value < self.other_args["min"]):
            raise ValueError(
                f"Invalid value to selected ({value}) should be in range: ["
                + f"{self.other_args['min']}, {self.other_args['max']}]"
            )
        self.changed = True
        self.other_args["selected"] = value


class ChoicesSelectorFormatter(SampleSelectorFormatter):
    def __init__(self, choices: List[str], **kwargs):
        super().__init__(**kwargs)
        if len(choices) == 0:
            raise RuntimeError(f"choices should have length at least 1!")
        self.other_args = dict(choices=choices, selected=choices[0])
        self.subtype = "choices"

    @property
    def selected(self) -> str:
        return self.other_args["selected"]

    @selected.setter
    def selected(self, value):
        if value not in self.other_args["choices"]:
            raise ValueError(
                f"Invalid value to selected ({value}), "
                + f"possibilities: {self.other_args['choices']}"
            )
        self.changed = True
        self.other_args["selected"] = value
