from llm_generation_server.formatters.format import FormattedContext, Formatter
from llm_generation_server.server import Server
from typing import Callable

class SampleSelectorFormatter(Formatter):
    def __init__(self, sample_min: int, sample_max: int, endpoint_url: str, endpoint_callback: Callable, **kwargs):
        super().__init__(**kwargs)
        self.sample_min = sample_min
        self.sample_max = sample_max
        self.endpoint_url = endpoint_url
        self.endpoint_callback = endpoint_callback
    
    def format(self):
        self.changed = False
        return FormattedContext(
            name=self.name,
            type="sample_selector",
            content=dict(
                min=self.sample_min,
                max=self.sample_max,
                address=self.endpoint_url
            ),
        )

    def add_endpoint(self, app: Server):
        app.add_endpoint(
            self.endpoint_url,
            self.endpoint_callback,
            methods=['POST']
        )