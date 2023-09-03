from typing import Callable, Dict, List, Set

from visuallm.component_base import ComponentBase
from visuallm.elements.element_base import ElementBase
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    SelectorSubElement,
)
from visuallm.server import Server


class ButtonElementStub(ButtonElement):
    """
    Stub that instead of real request json returns something that test user specifies.
    """

    def __init__(
        self,
        returned_response: Dict,
        processing_callback: Callable[[], None],
        name: str = "selector",
        subelements: List[SelectorSubElement] = ...,
        button_text="Select",
        **kwargs,
    ):
        super().__init__(processing_callback, name, subelements, button_text, **kwargs)
        self.returned_response = returned_response

    def get_response(self):
        return self.returned_response


class ParentComponentStub(ComponentBase):
    """Stub that has the same `fetch_info` method but nothing else."""

    def __init__(self, elements: List[ElementBase]):
        self.elements = elements
        self.registered_element_names: Set[str] = set()
        self.registered_elements: List[ElementBase] = []
        self.registered_url_endpoints: Set[str] = set()
        for element in self.elements:
            element.register_to_component(self)

    def register_to_server(self, server: Server):
        return None


def test_checkbox_selected_changed_set():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic CheckBox", default_value=False)

    def assert_not_updated():
        assert checkbox_subelement.updated is False

    def assert_updated():
        assert checkbox_subelement.updated is True

    assertion = lambda: None  # noqa: E731

    def processing_callback():
        assertion()

    button_element = ButtonElementStub(
        returned_response={checkbox_subelement.name: True},
        processing_callback=processing_callback,
        subelements=[checkbox_subelement],
    )
    parent_component = ParentComponentStub([button_element])

    # assert
    # when only fetching, it shouldn't be updated
    assertion = assert_not_updated
    returned_value = parent_component.fetch_info()
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )

    # when calling button element callback, the value is updated
    assertion = assert_updated
    returned_value = button_element.endpoint_callback()

    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is True
    )


def test_checkbox_selected_changed_not_set():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic CheckBox", default_value=False)

    def assert_not_updated():
        assert checkbox_subelement.updated is False

    button_element = ButtonElementStub(
        returned_response={checkbox_subelement.name: False},
        processing_callback=assert_not_updated,
        subelements=[checkbox_subelement],
    )
    parent_component = ParentComponentStub([button_element])

    # assert
    # when only fetching, it shouldn't be updated
    returned_value = parent_component.fetch_info()
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )

    # when calling button element callback, a new value is set but it is the
    # same as the old value
    returned_value = button_element.endpoint_callback()
    assert len(returned_value["elementDescriptions"]) == 0
