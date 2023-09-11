from typing import Callable, Dict, List, Sequence, Set

from visuallm.component_base import ComponentBase
from visuallm.elements.element_base import ElementBase
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
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

    def __init__(self, elements: Sequence[ElementBase]):
        self.elements = elements
        self.registered_element_names: Set[str] = set()
        self.registered_elements: List[ElementBase] = []
        self.registered_url_endpoints: Set[str] = set()
        for element in self.elements:
            element.order = 1
            element.register_to_component(self)

    def register_to_server(self, server: Server):
        return None


def test_checkbox_selected_changed_set():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic CheckBox", default_value=False)

    # this method tests what the user sees in the processing callback
    def assert_not_updated():
        assert checkbox_subelement.updated is False

    def assert_updated():
        assert checkbox_subelement.updated is True

    assertion = assert_not_updated

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

    # this method tests what the user sees in the processing callback
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


def test_multiple_subelements_nothing_changed():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic Checkbox", default_value=False)
    minmax_subelement = MinMaxSubElement(0, 20, "Frank")

    # this method tests what the user sees in the processing callback
    def assert_not_updated():
        assert checkbox_subelement.updated is False
        assert minmax_subelement.updated is False

    button_element = ButtonElementStub(
        returned_response={
            checkbox_subelement.name: False,
            minmax_subelement.name: 0,
        },
        processing_callback=assert_not_updated,
        subelements=[checkbox_subelement, minmax_subelement],
    )
    parent_component = ParentComponentStub([button_element])

    # assert
    returned_value = parent_component.fetch_info()
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == 0
    )

    returned_value = button_element.endpoint_callback()
    assert len(returned_value["elementDescriptions"]) == 0


def test_multiple_subelements_one_changed():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic Checkbox", default_value=False)
    minmax_subelement = MinMaxSubElement(0, 20, "Frank")

    # this method tests what the user sees in the processing callback
    def assert_not_updated():
        assert checkbox_subelement.updated is False
        assert minmax_subelement.updated is False

    def assert_updated():
        assert checkbox_subelement.updated is True
        assert minmax_subelement.updated is False

    assertion = lambda: None  # noqa: E731

    def processing_callback():
        assertion()

    button_element = ButtonElementStub(
        returned_response={
            checkbox_subelement.name: True,
            minmax_subelement.name: 0,
        },
        processing_callback=processing_callback,
        subelements=[checkbox_subelement, minmax_subelement],
    )
    parent_component = ParentComponentStub([button_element])

    # assert
    assertion = assert_not_updated
    returned_value = parent_component.fetch_info()
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == 0
    )

    assertion = assert_updated
    returned_value = button_element.endpoint_callback()
    assert len(returned_value["elementDescriptions"]) == 1

    # only one subelement is updated, however we still send all the subelement configs that
    # go with it
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is True
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == 0
    )


def test_multiple_subelements_both_changed():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic Checkbox", default_value=False)
    minmax_subelement = MinMaxSubElement(0, 20, "Frank")

    # this method tests what the user sees in the processing callback
    def assert_not_updated():
        assert checkbox_subelement.updated is False
        assert minmax_subelement.updated is False

    def assert_updated():
        assert checkbox_subelement.updated is True
        assert minmax_subelement.updated is True

    assertion = lambda: None  # noqa: E731

    def processing_callback():
        assertion()

    button_element = ButtonElementStub(
        returned_response={
            checkbox_subelement.name: True,
            minmax_subelement.name: 1,
        },
        processing_callback=processing_callback,
        subelements=[checkbox_subelement, minmax_subelement],
    )
    parent_component = ParentComponentStub([button_element])

    # assert
    assertion = assert_not_updated
    returned_value = parent_component.fetch_info()
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == 0
    )

    assertion = assert_updated
    returned_value = button_element.endpoint_callback()
    assert len(returned_value["elementDescriptions"]) == 1

    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is True
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == 1
    )


def test_multiple_subelements_other_one_changed():
    # arrange
    checkbox_subelement = CheckBoxSubElement("Basic Checkbox", default_value=False)
    choices_subelement = ChoicesSubElement(["one", "two"], "Choices")

    # this method tests what the user sees in the processing callback
    def assert_not_updated():
        assert checkbox_subelement.updated is False
        assert choices_subelement.updated is False

    def assert_updated():
        assert checkbox_subelement.updated is False
        assert choices_subelement.updated is True

    assertion = lambda: None  # noqa: E731

    def processing_callback():
        assertion()

    button_element = ButtonElementStub(
        returned_response={
            checkbox_subelement.name: False,
            choices_subelement.name: "two",
        },
        processing_callback=processing_callback,
        subelements=[checkbox_subelement, choices_subelement],
    )
    parent_component = ParentComponentStub([button_element])

    # assert
    assertion = assert_not_updated
    returned_value = parent_component.fetch_info()
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == "one"
    )

    assertion = assert_updated
    returned_value = button_element.endpoint_callback()
    assert len(returned_value["elementDescriptions"]) == 1

    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 2
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][0].configuration[
            "selected"
        ]
        is False
    )
    assert (
        returned_value["elementDescriptions"][0]["subelement_configs"][1].configuration[
            "selected"
        ]
        == "two"
    )
