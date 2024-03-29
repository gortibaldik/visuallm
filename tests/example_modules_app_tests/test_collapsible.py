import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/index.html#/"


def test_both_collapsibles_work(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    collapsible_buttons = firefox_driver.find_elements(By.CLASS_NAME, "collapsible")
    assert len(collapsible_buttons) == 3

    first_collapsible, second_collapsible, third_collapsible = collapsible_buttons
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 1

    first_collapsible.click()
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 2

    second_collapsible.click()
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 3

    first_collapsible.click()
    time.sleep(0.2)
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 2

    second_collapsible.click()
    time.sleep(0.2)
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 1

    third_collapsible.click()
    time.sleep(0.2)
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 0


def test_button_in_collapsible_works(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    collapsible_buttons = firefox_driver.find_elements(By.CLASS_NAME, "collapsible")
    assert len(collapsible_buttons) == 3

    first_collapsible, second_collapsible, third_collapsible = collapsible_buttons

    # open second collapsible in order to read the text
    second_collapsible.click()
    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    text_element = subcomponent.find_element(By.CLASS_NAME, "plainText")

    assert (
        text_element.text
        == "This is displayed in the collapsible element. Update: 0. MinMax: 0. Choices: first"
    )

    # close second collapsible
    second_collapsible.click()

    # open the first collapsible in order to click the button
    first_collapsible.click()

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    button_element = subcomponent.find_element(By.TAG_NAME, "button")
    # click the button
    button_element.click()

    # close the first collapsible
    first_collapsible.click()
    # open the second collapsible in order to check the text
    second_collapsible.click()

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    text_element = subcomponent.find_element(By.CLASS_NAME, "plainText")

    assert (
        text_element.text
        == "This is displayed in the collapsible element. Update: 1. MinMax: 0. Choices: first"
    )


def test_selector_has_the_correct_value(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    collapsible_buttons = firefox_driver.find_elements(By.CLASS_NAME, "collapsible")
    assert len(collapsible_buttons) == 3

    first_collapsible, second_collapsible, third_collapsible = collapsible_buttons
    first_collapsible.click()

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    min_max_selector = subcomponent.find_element(By.CLASS_NAME, "sample-selector")
    side_text = min_max_selector.find_element(By.CLASS_NAME, "selector-text")
    assert side_text.text == "Select Number"

    selector = min_max_selector.find_element(By.TAG_NAME, "input")
    assert selector.get_attribute("value") == "0"


def test_after_clicking_on_choices_collapsible_expands(
    app, firefox_driver: Firefox, link: str
):
    firefox_driver.get(link)

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    original_height = subcomponent.size["height"]

    choices_clickable = subcomponent.find_element(By.CLASS_NAME, "multiselect")
    choices_clickable.click()
    time.sleep(0.2)

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    new_height = subcomponent.size["height"]

    assert new_height > original_height

    other_text = subcomponent.find_element(By.CLASS_NAME, "multi-select-text")
    other_text.click()
    time.sleep(0.2)

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    new_height = subcomponent.size["height"]

    assert new_height == original_height


def test_during_waiting_collapsible_expands(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    original_height = subcomponent.size["height"]

    sample_selector_wrapper = subcomponent.find_element(
        By.CLASS_NAME, "sample-selector"
    )
    sample_selector = sample_selector_wrapper.find_element(By.TAG_NAME, "input")
    sample_selector.send_keys("10")

    button = subcomponent.find_element(By.TAG_NAME, "button")
    button.click()
    time.sleep(1)

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    new_height = subcomponent.size["height"]

    assert new_height > original_height
    time.sleep(3)

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    new_height = subcomponent.size["height"]

    assert new_height == original_height
