from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from .utils import sanitize_url


@dataclass
class ElementDescription:
    """The description of element contents.

    ## `name`
    - unique name of the element on the page

    ## `type`
    - type of the element, one of predefined types

    ## `configuration`
    - configuration values specific for each element
    """

    name: str
    type: str
    configuration: Dict


class ElementBase(ABC):
    """Base class for all elements in a single component. Element is a basic
    piece of information on the page, e.g. heading, table, selection input
    element...
    """

    def __init__(self, name: str):
        self._name = name
        self.changed = True

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @abstractmethod
    def construct_element_description(self) -> ElementDescription:
        ...

    @abstractmethod
    def add_endpoint(self, app):
        ...


class URLNamedWrapper:
    def __init__(self, internal_object, attr_name: str = "endpoint_url"):
        self.internal_object = internal_object
        self.attr_name = attr_name

    @property
    def name(self):
        return getattr(self.internal_object, self.attr_name)

    @name.setter
    def name(self, value: str):
        setattr(self.internal_object, self.attr_name, value)


class ElementWithEndpoint(ElementBase):
    def __init__(
        self,
        name: str,
        endpoint_callback: Callable,
        endpoint_url: Optional[str] = None,
    ):
        super().__init__(name)
        if endpoint_url is None:
            endpoint_url = sanitize_url(self.name)
        self.endpoint_url = endpoint_url
        self.endpoint_callback = endpoint_callback
        self.parent_component: Optional[Any] = None
        """The component that holds all the other elements. This is set
        in `ComponentBase.register_elements`
        """

    def get_url_named_wrapper(self):
        return URLNamedWrapper(self)
