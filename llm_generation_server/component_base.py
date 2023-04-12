from typing import List, Callable, Optional
from llm_generation_server.formatters.format import Formatter
from flask import jsonify
from pprint import pprint

class ComponentBase:
    def __init__(
        self,
        default_url: str,
        name: str,
        title: str,
        formatters: List[Formatter],
        default_callback: Optional[Callable] = None,
    ):
        self.default_url = default_url
        self.title = title
        self.name = name
        self.formatters = formatters
        if default_callback is None:
            default_callback = self.fetch_info
        self.default_callback = default_callback

    def init_app(self, app):
        self.app = app
        self.app.add_endpoint(
            self.default_url,
            self.default_callback,
            methods=['GET']
        )

        for formatter in self.formatters:
            formatter.add_endpoint(self.app)
    
    def fetch_info(self, fetch_all: bool=True, debug_print: bool=False):
        res = dict(
            result="success",
            contexts=[formatter.format() for formatter in self.formatters if formatter.changed or fetch_all]
        )
        if debug_print:
            pprint(res)
        return jsonify(res)

    
