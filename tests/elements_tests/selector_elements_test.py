from tests.elements_tests.custom_request_mixin import CustomRequestMixin
from visuallm.component_base import ComponentBase
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
)


class ButtonElementStub(CustomRequestMixin, ButtonElement):
    """
    Stub that instead of real request json returns something that test user specifies.
    """


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
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

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
    assert "elementDescriptions" in returned_value
    element_descriptions = returned_value["elementDescriptions"]
    assert len(element_descriptions) == 1
    assert "subelement_configs" in element_descriptions[0]
    subelement_configs = element_descriptions[0]["subelement_configs"]
    assert len(subelement_configs) == 1

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
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

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
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

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
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

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
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

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
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

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


def test_on_button_name_change():
    # arrange
    button_element = ButtonElementStub(
        returned_response={},
        processing_callback=lambda: None,
        subelements=[],
        button_text="Select",
    )
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

    # assert
    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 0
    assert returned_value["elementDescriptions"][0]["button_text"] == "Select"

    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 0

    button_element.button_text = "Regenerate"
    assert button_element.changed is True

    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 0
    assert returned_value["elementDescriptions"][0]["button_text"] == "Regenerate"


def test_on_button_disabled_change():
    # arrange
    button_element = ButtonElementStub(
        returned_response={},
        processing_callback=lambda: None,
        subelements=[],
        button_text="Select",
        disabled=False,
    )
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

    # assert
    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 0
    assert returned_value["elementDescriptions"][0]["disabled"] is False

    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 0

    button_element.disabled = True
    assert button_element.changed is True

    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    assert len(returned_value["elementDescriptions"][0]["subelement_configs"]) == 0
    assert returned_value["elementDescriptions"][0]["disabled"] is True
