from __future__ import annotations

from pprint import pprint
from typing import TYPE_CHECKING, Callable, List, MutableSet, Optional

if TYPE_CHECKING:
    from .elements.element_base import ElementBase
    from visuallm.server import Server

from flask import jsonify

from .elements.utils import register_named, sanitize_url
from .named import Named, NamedWrapper


class ComponentBase(Named):
    def __init__(
        self,
        name: str,
        title: str,
        elements: List[ElementBase],
        default_url: Optional[str] = None,
        default_callback: Optional[Callable] = None,
    ):
        super().__init__(name)
        if default_url is None:
            default_url = sanitize_url(name)
        self.default_url = default_url
        self.title = title

        # register all elements to component structures
        self.registered_element_names = set()
        self.registered_elements: List[ElementBase] = []
        self.registered_url_endpoints: MutableSet[str] = set()
        for element in elements:
            element.register_to_component(self)

        if default_callback is None:
            default_callback = self.fetch_info
        self.default_callback = default_callback

    def register_to_server(self, server: Server):
        for element in self.registered_elements:
            # ensure that there are no two elements sharing the same url
            element.register_to_server(server)

        # ensure that there are no two components sharing the same name
        register_named(self, server.registered_component_names)

        # ensure that there are no two components sharing the same default url
        register_named(NamedWrapper(self, "default_url"), server.registered_urls)
        server.add_endpoint(self.default_url, self.default_callback, methods=["GET"])

    def fetch_info(self, fetch_all: bool = True, debug_print: bool = False):
        res = dict(
            result="success",
            elementDescriptions=[
                element.construct_element_description()
                for element in self.registered_elements
                if element.changed or fetch_all
            ],
        )
        if debug_print:
            pprint(res)
        return jsonify(res)
