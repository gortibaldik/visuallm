import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/index.html#/text_input_component"


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
    expected_text_value = "Some short text."
    form = firefox_driver.find_elements(By.TAG_NAME, "form")[2]
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(expected_text_value)
    text_element = firefox_driver.find_elements(By.CLASS_NAME, "plainText")[-1]

    button = form.find_element(By.TAG_NAME, "button")
    button.click()

    assert expected_text_value == textarea.get_attribute("value")
    assert text_element.text == expected_text_value


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
    text_element = firefox_driver.find_elements(By.CLASS_NAME, "plainText")[-1]

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


def test_special_text_shown_correctly_escaped(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)

    test_text_value = "<div>Very Special Text</div>"
    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(test_text_value)
    button = form.find_element(By.TAG_NAME, "button")
    button.click()
    wrap_elems = firefox_driver.find_elements(By.CLASS_NAME, "wrapElement")
    assert wrap_elems[1].text == test_text_value


def test_enter_can_be_used_to_send_text(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)

    expected_value = "Some short text."
    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.clear()
    textarea.send_keys(expected_value)
    textarea.send_keys(Keys.ENTER)

    time.sleep(0.05)
    wrap_elems = firefox_driver.find_elements(By.CLASS_NAME, "wrapElement")
    assert wrap_elems[1].text == expected_value


def test_shift_enter_can_be_used_to_enter_newline(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)

    expected_value1 = "Some short text line 1"
    expected_value2 = "Some short text line 2"

    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.send_keys(expected_value1)
    ActionChains(firefox_driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).perform()
    textarea.send_keys(expected_value2)

    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")

    actual_text = textarea.get_attribute("value")
    assert actual_text == expected_value1 + "\n" + expected_value2


def test_shift_enter_then_enter_to_submit(app, firefox_driver: Firefox, link):
    firefox_driver.get(link)

    expected_value1 = "Some short text line 1"
    expected_value2 = "Some short text line 2"

    form = firefox_driver.find_element(By.TAG_NAME, "form")
    textarea = form.find_element(By.TAG_NAME, "textarea")
    textarea.clear()
    textarea.send_keys(expected_value1)

    # add newline to textarea
    ActionChains(firefox_driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).perform()
    ActionChains(firefox_driver).key_up(Keys.SHIFT).perform()

    # write another line of text
    textarea.send_keys(expected_value2)

    # send the text to the backend
    textarea.send_keys(Keys.ENTER)
    time.sleep(0.2)

    wrap_elems = firefox_driver.find_elements(By.CLASS_NAME, "wrapElement")
    assert wrap_elems[1].text == expected_value1 + "\n" + expected_value2
