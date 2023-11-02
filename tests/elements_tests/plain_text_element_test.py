import pytest

from visuallm import ComponentBase
from visuallm.elements import PlainTextElement


def test_escaping_of_gt_lt():
    element = PlainTextElement()
    element.content = "<br /> <div> <div/>"

    assert element.content == "&lt;br /&gt; &lt;div&gt; &lt;div/&gt;"


def test_newline_conversion():
    element = PlainTextElement()
    element.content = """This is a text
with multiple lines
exactly three lines are used"""

    assert (
        element.content
        == "This is a text<br />with multiple lines<br />exactly three lines are used"
    )


def test_non_sane_text_at_element_construction_time():
    element = PlainTextElement()
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(element)
    element._content = "<script>reallyMaliciousFunction()</script>"

    with pytest.raises(ValueError, match="is not allowed value of PlainText element."):
        parent_component.fetch_info()


def test_doesnt_throw_anything_on_fine_text():
    element = PlainTextElement()
    parent_component = ComponentBase(name="base", title="base")
    parent_component.add_element(element)

    element.content = "<script>Good escaped string</script>"
    info = parent_component.fetch_info()

    element_descriptions = info["elementDescriptions"]
    assert len(element_descriptions) == 1
    assert (
        element_descriptions[0]["value"]
        == "&lt;script&gt;Good escaped string&lt;/script&gt;"
    )
