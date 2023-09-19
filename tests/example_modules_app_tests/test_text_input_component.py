import pytest
from selenium.webdriver.common.by import By


@pytest.fixture()
def link():
    return "http://localhost:5000/index.html#/text_input_component"


def test_insert_text_in_textarea(app, firefox_driver, link):
    firefox_driver.get(link)
    test_text_value = "Some short text."
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    elem.send_keys(test_text_value)
    assert test_text_value == elem.get_attribute("value")


def test_textarea_cleared_after_form_submission(app, firefox_driver, link):
    firefox_driver.get(link)
    test_text_value = "Some short text."
    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(test_text_value)
    button = form.find_element(By.TAG_NAME, "button")
    button.click()
    assert textarea.get_attribute("value") == ""


def test_text_shown_in_wrap_element_after_form_submission(app, firefox_driver, link):
    firefox_driver.get(link)

    test_text_value = "Some short text."
    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(test_text_value)
    button = form.find_element(By.TAG_NAME, "button")
    button.click()
    wrap_elem = firefox_driver.find_element(By.CLASS_NAME, "wrapElement")
    assert wrap_elem.text == test_text_value
