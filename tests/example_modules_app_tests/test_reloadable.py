import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://127.0.0.1:{port}/index.html#/reloadable_component"


def test_reload_1(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)
    expected_descriptions = [
        'When you click on the "Reload" button, the page will reload with new elements.',
        (
            "The page was reloaded!\n"
            "(Click on Reload button in under the Button Back to go back to the previous page)"
        ),
    ]

    button = firefox_driver.find_element(By.TAG_NAME, "button")
    assert button.text == "Reload"

    description = firefox_driver.find_element(By.CLASS_NAME, "plainText")
    assert description.text == expected_descriptions[0]

    button.click()
    time.sleep(0.1)

    description = firefox_driver.find_element(By.CLASS_NAME, "plainText")
    assert description.text == expected_descriptions[1]


def test_reload_2(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)
    expected_descriptions = [
        'When you click on the "Reload" button, the page will reload with new elements.',
        (
            "The page was reloaded!\n"
            "(Click on Reload button in under the Button Back to go back to the previous page)"
        ),
    ]
    # find the expected description
    description = firefox_driver.find_element(By.CLASS_NAME, "plainText")
    assert description.text == expected_descriptions[1]

    # find collapsible and open it
    button = firefox_driver.find_element(By.TAG_NAME, "button")
    assert button.text == "Button Back"
    button.click()
    time.sleep(0.1)

    collapsible = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    button = collapsible.find_element(By.TAG_NAME, "button")

    button.click()
    time.sleep(0.1)

    description = firefox_driver.find_element(By.CLASS_NAME, "plainText")
    assert description.text == expected_descriptions[0]
