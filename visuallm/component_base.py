from __future__ import annotations

from collections.abc import Callable, MutableSet
from pprint import pprint
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from visuallm.elements.element_base import ElementBase
    from visuallm.server import Server

from abc import ABCMeta

from visuallm.elements.utils import register_named, sanitize_url
from visuallm.named import Named, NamedWrapper


class ComponentMetaclass(ABCMeta):

    """Inheritor of ComponentBaseMetaclass which adds call to
    __post_init__ after all the inits were executed and an inheritor of
    ABCMeta.
    """

    def __call__(cls, *args, **kwargs):
        """Add __post_init__ call right after all the constructor of all the inheritors are called"""
        obj = super().__call__(*args, **kwargs)
        if hasattr(obj, "__post_init__"):
            obj.__post_init__(*args, **kwargs)
        return obj


class ComponentBase(Named, metaclass=ComponentMetaclass):
    def __init__(
        self,
        name: str,
        title: str,
        default_url: str | None = None,
        default_callback: Callable | None = None,
    ):
        super().__init__(name)
        if default_url is None:
            default_url = sanitize_url(name)
        if default_callback is None:
            default_callback = self.fetch_info

        self.default_url = default_url
        self.title = title

        # register all elements to component structures
        self.registered_element_names: set[str] = set()
        self.registered_elements: list[ElementBase] = []
        self.registered_url_endpoints: MutableSet[str] = set()

        self.default_callback = default_callback
        self._already_fetched = False

    def __post_init__(self, *args, **kwargs):
        pass

    def _get_order(self, order: float | None) -> float:
        if order is None:
            if len(self.registered_elements) == 0:
                currently_biggest_priority = 0.0
            else:
                currently_biggest_priority = max(
                    e.order for e in self.registered_elements
                )
            order = currently_biggest_priority + 1
        return order

    def add_element(self, element: ElementBase, order: float | None = None):
        """Add element to the list of frontend-rendered elements.

        The page is organized from top to bottom. Each element either receives
        the order automatically (it is appended at the end, top-most element
        has order 1, the bottom-most element has order `len(elements)`), or you
        can optionally specify order, to put the element on the other position
        in the list.

        Args:
        ----
            element (ElementBase): element to be added to frontend-rendered elements.
            order (float | None, optional): Optional order of the element in the
                list of frontend-rendered elements. Defaults to None.

        Raises:
        ------
            RuntimeError: each element may be registered to at most one component,
                if you try to register the element into multiple componnets, this
                exception is raised.
        """
        if element.is_registered_to_component:
            raise RuntimeError(
                f"Element with name: {element.name} is already registered to some component!"
            )
        if self._already_fetched:
            raise RuntimeError(
                "After first fetch, Flask doesn't support adding any new elements! "
                "(limitation of add_url_rule)"
            )
        order = self._get_order(order)
        element.register_to_component(self)
        element.order = order

    def add_elements(self, elements: list[ElementBase], order: float | None = None):
        order = self._get_order(order)
        for element in elements:
            self.add_element(element, order)

    def clear_elements(self):
        """Do not show any elements on the frontend.

        During the call, the `is_displayed` property on all the registered elements
        is set to `False`.
        """
        for element in self.registered_elements:
            element.unset_displayed()

    def register_to_server(self, server: Server):
        for element in self.registered_elements:
            # ensure that there are no two elements sharing the same url
            element.register_to_server(server)

        # ensure that there are no two components sharing the same name
        register_named(self, server.registered_component_names)

        # ensure that there are no two components sharing the same default url
        register_named(NamedWrapper(self, "default_url"), server.registered_urls)
        server.add_endpoint(self.default_url, self.default_callback, methods=["GET"])

    def fetch_info(
        self, fetch_all: bool = True, debug_print: bool = False
    ) -> dict[str, Any]:
        self._already_fetched = True
        res = {
            "result": "success",
            "elementDescriptions": [
                element.construct_element_description()
                for element in sorted(self.registered_elements, key=lambda e: e.order)
                if _element_should_be_displayed(element, fetch_all)
            ],
        }
        if debug_print:
            pprint(res)
        return res

    def fetch_exception(self, traceback: str) -> dict[str, Any]:
        self._already_fetched = True
        res = {"result": "exception", "reason": traceback}
        return res


def _element_should_be_displayed(element: ElementBase, fetch_all: bool):
    if not element.is_displayed:
        return False

    return element.changed or fetch_all
