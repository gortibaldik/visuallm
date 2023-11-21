import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/index.html#/"


def test_can_be_run(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    collapsible = firefox_driver.find_element(By.CLASS_NAME, "collapsible")
    collapsible.click()
    time.sleep(0.2)

    content = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    form = content.find_element(By.TAG_NAME, "form")
    subselectors = form.find_element(
        By.CLASS_NAME, "subSelectorsWrapper"
    ).find_elements(By.CLASS_NAME, "wrapElement")

    assert len(subselectors) == 2

    subselectors[1].send_keys(Keys.DOWN)
    subselectors[1].send_keys(Keys.ENTER)
    ActionChains(firefox_driver).send_keys(Keys.ENTER).perform()

    content = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    form = content.find_element(By.TAG_NAME, "form")
    subselectors = form.find_element(
        By.CLASS_NAME, "subSelectorsWrapper"
    ).find_elements(By.CLASS_NAME, "wrapElement")

    assert len(subselectors) == 3

    subselectors[2].click()
    # select value 0
    ActionChains(firefox_driver).send_keys(Keys.ENTER).perform()
    # send value to backend
    ActionChains(firefox_driver).send_keys(Keys.ENTER).perform()
    time.sleep(0.2)

    content = firefox_driver.find_element(By.CLASS_NAME, "subcomponent")
    form = content.find_element(By.TAG_NAME, "form")
    subselectors = form.find_element(
        By.CLASS_NAME, "subSelectorsWrapper"
    ).find_elements(By.CLASS_NAME, "wrapElement")

    assert len(subselectors) == 2
