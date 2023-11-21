import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://127.0.0.1:{port}/index.html#/selector_change_component"


def test_on_change_selectors_change(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    forms = firefox_driver.find_elements(By.TAG_NAME, "form")
    assert len(forms) == 2

    # two selectors are visible
    selector_form = forms[0].find_element(By.CLASS_NAME, "subSelectorsWrapper")
    assert len(selector_form.find_elements(By.CLASS_NAME, "wrapElement")) == 2

    change_button = forms[1].find_element(By.TAG_NAME, "button")
    change_button.click()
    time.sleep(0.2)

    # assert that only one is visible
    forms = firefox_driver.find_elements(By.TAG_NAME, "form")
    assert len(forms) == 2

    # two selectors are visible
    selector_form = forms[0].find_element(By.CLASS_NAME, "subSelectorsWrapper")
    assert len(selector_form.find_elements(By.CLASS_NAME, "wrapElement")) == 1

    change_button = forms[1].find_element(By.TAG_NAME, "button")
    change_button.click()
    time.sleep(0.2)

    forms = firefox_driver.find_elements(By.TAG_NAME, "form")
    assert len(forms) == 2

    # one selector are visible
    selector_form = forms[0].find_element(By.CLASS_NAME, "subSelectorsWrapper")
    assert len(selector_form.find_elements(By.CLASS_NAME, "wrapElement")) == 2
