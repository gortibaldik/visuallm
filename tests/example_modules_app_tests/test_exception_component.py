import time

import pytest
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/index.html#/selector_failing_component"


def test_after_button_press_alert_raised(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    elem = firefox_driver.find_element(By.TAG_NAME, "button")
    elem.click()
    time.sleep(0.1)
    alert = firefox_driver.switch_to.alert

    assert "RuntimeError: Runtime error raised on purpose!" in alert.text

    alert.accept()
    time.sleep(0.1)

    with pytest.raises(NoAlertPresentException):
        firefox_driver.switch_to.alert  # noqa: B018
