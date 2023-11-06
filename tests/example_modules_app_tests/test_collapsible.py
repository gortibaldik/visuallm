import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/index.html#/"


def test_both_collapsibles_work(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    collapsible_buttons = firefox_driver.find_elements(By.CLASS_NAME, "collapsible")
    assert len(collapsible_buttons) == 2

    first_collapsible, second_collapsible = collapsible_buttons
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 0

    first_collapsible.click()
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 1

    second_collapsible.click()
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 2

    first_collapsible.click()
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 1

    second_collapsible.click()
    collapsible_contents = firefox_driver.find_elements(By.CLASS_NAME, "subcomponent")
    assert len(collapsible_contents) == 0


def test_button_in_collapsible_works(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    collapsible_buttons = firefox_driver.find_elements(By.CLASS_NAME, "collapsible")
    assert len(collapsible_buttons) == 2

    first_collapsible, second_collapsible = collapsible_buttons

    second_collapsible.click()
    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    text_element = subcomponent.find_element(By.CLASS_NAME, "plainText")

    assert (
        text_element.text == "This is displayed in the collapsible element. Update: 0"
    )

    second_collapsible.click()
    first_collapsible.click()

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    button_element = subcomponent.find_element(By.TAG_NAME, "button")
    button_element.click()

    first_collapsible.click()
    second_collapsible.click()

    subcomponent = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    text_element = subcomponent.find_element(By.CLASS_NAME, "plainText")

    assert (
        text_element.text == "This is displayed in the collapsible element. Update: 1"
    )
