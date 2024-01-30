from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol

from flask import request

from visuallm.named import Named, NamedWrapper

from .utils import register_named, sanitize_url

if TYPE_CHECKING:
    from visuallm.component_base import ComponentBase
    from visuallm.server import Server


class OnElementChanged(Protocol):
    def __call__(self):
        ...


class ElementBase(Named, ABC):

    """Base class for all elements in a single component. Element is a basic
    piece of information on the page, e.g. heading, table, selection input
    element...
    """

    def __init__(
        self,
        name: str,
        type: str,
        on_element_changed_callback: OnElementChanged | None = None,
    ):
        """Base class for all elements with counterparts in the frontend.

        Args:
        ----
            name (str): name of the element, unique identifier of the element
                in the component. If you name multiple components the same,
                the library appends number after the element.
            type (str): string that matches the backend element to the
                frontend element.
            on_element_changed_callback (OnElementChanged, optional): callback
                called anytime a change in the element's value is detected
        """
        super().__init__(name)
        self._type = type
        self._order: float | None = None
        self._changed = True
        self._is_registered_to_component: bool = False
        self.on_element_changed_callback = on_element_changed_callback
        self._is_displayed = True

    @property
    def is_displayed(self):
        """Should the element be displayed on the frontend ?"""
        return self._is_displayed

    def unset_displayed(self):
        """After the call, the element wouldn't be displayed on the frontend."""
        self._is_displayed = False

    def set_displayed(self):
        """After the call, the element would be displayed on the frontend."""
        self.set_changed()
        self._is_displayed = True

    @property
    def is_registered_to_component(self):
        return self._is_registered_to_component

    @property
    def changed(self):
        return self._changed

    def set_changed(self):
        self._changed = True
        if self.on_element_changed_callback is not None:
            self.on_element_changed_callback()

    @property
    def order(self) -> float:
        """Priority of the elements displayed on the frontend.
        The lowest order is on the top of the page, the highest on the bottom.
        """
        if self._order is None:
            raise RuntimeError("Order wasn't assigned yet!")
        return self._order

    @order.setter
    def order(self, value: float):
        if value <= 0:
            raise ValueError("The priority can be only positive float")
        self._order = value

    @property
    def type(self):
        return self._type

    def construct_element_description(self) -> dict[str, Any]:
        """Construct description of all the parts of the element to be
        displayed on the frontend.

        Sets changed to false!
        """
        self._changed = False
        return dict(
            name=self.name,
            type=self.type,
            **self.construct_element_configuration(),
        )

    @abstractmethod
    def construct_element_configuration(self) -> dict[str, Any]:
        """Construct the message with all the parts needed to recreate the
        same state of the element on the frontend
        """
        pass

    def register_to_server(self, server: Server):
        """Register the element's endpoint to the server

        Args:
        ----
            server (Server): the server to which the element is registered.
        """
        # by default nothing is registered
        pass

    def register_to_component(self, component: ComponentBase):
        """Registers the element to the component by ensuring
        that there isn't any other element which has the same name
        and if there is, change the name of this element by appending
        a number after it (e.g. naming the elements with the same name
        in order of registration to the component `c`, `c_1`, `c_2`, `c_3`,
        ...)
        """
        register_named(
            self, component.registered_element_names, component.registered_elements
        )
        self._is_registered_to_component = True


class ElementWithEndpoint(ElementBase):
    def __init__(
        self,
        name: str,
        type: str,
        endpoint_url: str | None = None,
    ):
        """Base class for all elements with counterparts in the frontend that
        can send data to the backend

        Args:
        ----
            name (str): name of the element, unique identifier of the element
                in the component. If you name multiple components the same,
                the library appends number after the element.
            type (str): string that matches the backend element to the
                frontend element.
            endpoint_url (str, optional): url of the endpoint that the
                frontend will call when communicating with this element. If
                it is None, then a sanitized version of `name` will be used.
        """
        super().__init__(name, type)
        if endpoint_url is None:
            endpoint_url = sanitize_url(self.name)
        self.endpoint_url = endpoint_url
        self._parent_component: ComponentBase | None = None
        """The component that holds all the other elements. This is set
        in `ComponentBase.register_elements`
        """
        self._type = type

    @property
    def parent_component(self) -> ComponentBase:
        if self._parent_component is None:
            raise RuntimeError(
                "Parent Component accessed, but it was never assigned any value !"
            )
        return self._parent_component

    def get_request_dict(self) -> dict:
        """Get the request dict from the api call.

        Written in this way for better testability (changing the api call flask
        logic with custom request dict for test cases)

        Raises
        ------
            RuntimeError: if the api call dict doesn't contain a json object
        """
        if not request.is_json:
            raise RuntimeError("The data in request should be json!")
        return request.get_json()

    @abstractmethod
    def endpoint_callback(self):
        """Method that is called when the frontend sends data to the backend."""
        pass

    def construct_element_description(self) -> dict[str, Any]:
        return_dict = super().construct_element_description()
        return_dict["address"] = self.endpoint_url.removeprefix("/")
        return return_dict

    def register_to_server(self, server: Server):
        """Register the element's endpoint to the server.

        Args:
        ----
            server (Server): server which will hold the endpoint to this element
        """
        register_named(NamedWrapper(self, "endpoint_url"), server.registered_urls)
        server.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])

    def register_to_component(self, component: ComponentBase):
        super().register_to_component(component)
        register_named(
            NamedWrapper(self, "endpoint_url"), component.registered_url_endpoints
        )
        self._parent_component = component
