import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link():
    return "http://localhost:5000/index.html#/text_input_component"


def test_insert_text_in_textarea(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)
    test_text_value = "Some short text."
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    elem.send_keys(test_text_value)
    assert test_text_value == elem.get_attribute("value")


def test_textarea_cleared_after_form_submission(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)
    test_text_value = "Some short text."
    form = firefox_driver.find_elements(By.TAG_NAME, "form")[0]
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(test_text_value)
    button = form.find_element(By.TAG_NAME, "button")
    button.click()
    assert textarea.get_attribute("value") == ""


def test_textarea_stays_after_form_submission(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)
    test_text_value = "Some short text."
    form = firefox_driver.find_elements(By.TAG_NAME, "form")[2]
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(test_text_value)
    text_element = firefox_driver.find_elements(By.TAG_NAME, "div")[-1]

    button = form.find_element(By.TAG_NAME, "button")
    button.click()

    assert textarea.get_attribute("value") == test_text_value
    assert text_element.text == test_text_value


def test_textarea_stays_after_reload_of_page(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)
    test_text_value = "Some short text."
    form = firefox_driver.find_elements(By.TAG_NAME, "form")[2]
    textarea = form.find_element(By.TAG_NAME, "textarea")

    textarea.clear()
    textarea.send_keys(test_text_value)
    text_element = firefox_driver.find_elements(By.TAG_NAME, "div")[-1]

    button = form.find_element(By.TAG_NAME, "button")
    button.click()

    firefox_driver.refresh()
    form = firefox_driver.find_elements(By.TAG_NAME, "form")[2]
    textarea = form.find_element(By.TAG_NAME, "textarea")
    text_element = firefox_driver.find_elements(By.TAG_NAME, "div")[-1]

    assert textarea.get_attribute("value") == test_text_value
    assert text_element.text == test_text_value


def test_text_shown_in_wrap_element_after_form_submission(
    app, firefox_driver: Firefox, link
):
    firefox_driver.get(link)

    test_text_value = "Some short text."
    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(test_text_value)
    button = form.find_element(By.TAG_NAME, "button")
    button.click()
    wrap_elems = firefox_driver.find_elements(By.CLASS_NAME, "wrapElement")
    assert wrap_elems[1].text == test_text_value
