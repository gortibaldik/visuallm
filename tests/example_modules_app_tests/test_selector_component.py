import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# pytest runs the tests in the same order that they're found in the test module, hence
# we just need to ensure that the tests follow the state left on the server


@pytest.fixture()
def link():
    return "http://127.0.0.1:5000/index.html#/selector_component"


def test_text_before_any_input(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    elem = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
    assert (
        elem.text
        == "This library is super and I would give it 0 stars out of 0 if I could. (First Message)"
    )


def test_nothing_changed(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    button_elem = firefox_driver.find_element(by=By.TAG_NAME, value="button")
    button_elem.click()

    text_elem = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
    assert (
        text_elem.text
        == "This library is super and I would give it 0 stars out of 0 if I could. (Don't take me seriously.) This has not changed!"
    )


def test_select_number(app, firefox_driver: Firefox, link: str):
    for i in range(1, 11):
        firefox_driver.get(link)

        number_elem_parent = firefox_driver.find_element(
            by=By.CLASS_NAME, value="selector-wrapper"
        )
        number_elem = number_elem_parent.find_element(by=By.TAG_NAME, value="input")
        number_elem.send_keys(Keys.ARROW_UP)
        button_elem = firefox_driver.find_element(by=By.TAG_NAME, value="button")
        button_elem.click()

        text_elem = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
        assert (
            f"This library is super and I would give it {i} stars out of {i} if I could. (Don't take me seriously.) This has changed!"
            == text_elem.text
        )


def test_select_choices(app, firefox_driver: Firefox, link: str):
    choices = ["magnificent", "incredible", "super"]
    for choice in choices:
        firefox_driver.get(link)

        choices_elem = firefox_driver.find_element(
            by=By.CLASS_NAME, value="multi-select-wrapper"
        )
        choices_elem.click()
        choices_elem.send_keys(Keys.ARROW_DOWN)

        button_elem = firefox_driver.find_element(by=By.TAG_NAME, value="button")
        button_elem.click()

        text_elem = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
        assert (
            f"This library is {choice} and I would give it 10 stars out of 10 if I could. (Don't take me seriously.) This has changed!"
            == text_elem.text
        )


def test_checkbox(app, firefox_driver: Firefox, link: str):
    expected_text = "(Don't take me seriously.) This has not changed!"
    for i in range(2):
        firefox_driver.get(link)

        checkbox_parent_elem = firefox_driver.find_element(
            by=By.CLASS_NAME, value="checkbox-wrapper"
        )
        checkbox_elem = checkbox_parent_elem.find_element(by=By.TAG_NAME, value="input")

        if i == 1:
            checkbox_elem.click()
            expected_text = "(I say it as a well-relaxed man!) This has changed!"

        button_elem = firefox_driver.find_element(by=By.TAG_NAME, value="button")
        button_elem.click()

        text_elem = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
        assert (
            f"This library is super and I would give it 10 stars out of 10 if I could. {expected_text}"
            == text_elem.text
        )
