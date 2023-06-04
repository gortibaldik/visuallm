from pprint import pprint
from typing import Callable, List, MutableSet, Optional, Union

from flask import jsonify

from .elements.element_base import ElementBase, ElementWithEndpoint, URLNamedWrapper
from .elements.utils import register_named, sanitize_url


class ComponentBase:
    def __init__(
        self,
        name: str,
        title: str,
        elements: List[ElementBase],
        default_url: Optional[str] = None,
        default_callback: Optional[Callable] = None,
    ):
        if default_url is None:
            default_url = sanitize_url(name)
        self.default_url = default_url
        self.title = title
        self.name = name

        self.registered_element_names = set()
        self.registered_elements: List[ElementBase] = []

        self.registered_url_endpoints: MutableSet[str] = set()

        self.register_elements(elements)
        if default_callback is None:
            default_callback = self.fetch_info
        self.default_callback = default_callback

    def init_app(self, app):
        for element in self.registered_elements:
            # ensure that there are no two elements sharing the same url
            if isinstance(element, ElementWithEndpoint):
                register_named(element.get_url_named_wrapper(), app.registered_urls)
            element.add_endpoint(app)

        # ensure that there are no two components shared the same name
        register_named(self, app.registered_component_names)

        # ensure that there are no two components sharing the same default url
        register_named(URLNamedWrapper(self, "default_url"), app.registered_urls)
        app.add_endpoint(self.default_url, self.default_callback, methods=["GET"])

    def register_elements(
        self, elements: List[Union[ElementBase, ElementWithEndpoint]]
    ):
        for element in elements:
            # ensure that each element has a different name
            register_named(
                element, self.registered_element_names, self.registered_elements
            )

            if isinstance(element, ElementWithEndpoint):
                # ensure that there are no two url endpoints with the same name
                register_named(
                    element.get_url_named_wrapper(), self.registered_url_endpoints
                )
                element.parent_component = self

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
