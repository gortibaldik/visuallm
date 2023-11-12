from tests.elements_tests.custom_request_mixin import CustomRequestMixin
from visuallm import ComponentBase
from visuallm.elements import ButtonElement
from visuallm.elements.selector_elements import TextInputSubElement


class ButtonElementStub(CustomRequestMixin, ButtonElement):

    """Stub that instead of real request json returns something that test user specifies"""


def test_on_text_input_change():
    # arrange
    def processing_callback(text_input_element: ButtonElement):
        assert text_input_element.changed is True

    text_input_element = TextInputSubElement(blank_after_text_send=True)
    button_element = ButtonElementStub(
        returned_response={text_input_element.name: "Something"},
        processing_callback=lambda: processing_callback(button_element),
        button_text="Select",
        subelements=[text_input_element],
    )
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

    # assert
    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    button_config = returned_value["elementDescriptions"][0]
    assert len(button_config["subelement_configs"]) == 1
    text_input_config = button_config["subelement_configs"][0].configuration
    assert text_input_config["selected"] == ""

    returned_value = button_element.endpoint_callback()
    assert len(returned_value["elementDescriptions"]) == 1
    button_config = returned_value["elementDescriptions"][0]
    assert len(button_config["subelement_configs"]) == 1
    text_input_config = button_config["subelement_configs"][0].configuration
    assert text_input_config["selected"] == ""
    assert text_input_element.value_from_frontend == "Something"


def test_on_button_text_change():
    # arrange
    text_input_element = TextInputSubElement(blank_after_text_send=True)
    button_element = ButtonElementStub(
        returned_response={"text_input": "Something"},
        processing_callback=lambda: None,
        button_text="Select",
        subelements=[text_input_element],
    )
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(button_element)

    # assert
    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    button_config = returned_value["elementDescriptions"][0]
    assert len(button_config["subelement_configs"]) == 1
    text_input_config = button_config["subelement_configs"][0].configuration

    assert text_input_config["selected"] == ""

    button_element.button_text = "Regenerate"
    assert button_element.changed is True

    returned_value = button_element.endpoint_callback()
    assert button_element.changed is False
    assert len(returned_value["elementDescriptions"]) == 1
    button_config = returned_value["elementDescriptions"][0]
    assert button_config["button_text"] == "Regenerate"

    text_input_config = button_config["subelement_configs"][0].configuration
    assert text_input_config["selected"] == ""
