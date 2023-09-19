from tests.elements_tests.custom_request_mixin import CustomRequestMixin
from visuallm import ComponentBase
from visuallm.elements import TextInputElement


class TextInputElementStub(CustomRequestMixin, TextInputElement):
    """
    Stub that instead of real request json returns something that test user specifies
    """


def test_on_text_input_change():
    # arrange
    def processing_callback(text_input_element: TextInputElement):
        assert text_input_element.changed is True

    text_input_element = TextInputElementStub(
        returned_response={"text_input": "Something"},
        processing_callback=lambda: processing_callback(text_input_element),
        button_text="Select",
        blank_text_after_send=False,
    )
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(text_input_element)

    # assert
    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    assert returned_value["elementDescriptions"][0]["text_input"] == ""

    # TODO: end asserts
    returned_value = text_input_element.endpoint_callback()
    assert returned_value["elementDescriptions"][0]["text_input"] == "Something"


def test_on_button_text_change():
    # arrange
    text_input_element = TextInputElementStub(
        returned_response={"text_input": ""},
        processing_callback=lambda: None,
        button_text="Select",
    )
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(text_input_element)

    # assert
    returned_value = parent_component.fetch_info(fetch_all=False)
    assert len(returned_value["elementDescriptions"]) == 1
    assert returned_value["elementDescriptions"][0]["text_input"] == ""

    text_input_element.button_text = "Regenerate"
    assert text_input_element.changed is True

    returned_value = text_input_element.endpoint_callback()
    assert text_input_element.changed is False
    assert len(returned_value["elementDescriptions"]) == 1
    assert returned_value["elementDescriptions"][0]["button_text"] == "Regenerate"
    assert returned_value["elementDescriptions"][0]["text_input"] == ""
