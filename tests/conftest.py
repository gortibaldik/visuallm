import subprocess

import pytest
from selenium import webdriver


@pytest.fixture(scope="session")
def firefox_driver():
    """Create a selenium webdriver with firefox
    and runs it for the duration of whole module, and closes it after
    the last test in the module

    Yields
    ------
        selenium.webdriver.Firefox
    """
    opts = webdriver.FirefoxOptions()
    opts.add_argument("--headless")
    service = webdriver.FirefoxService(log_output=subprocess.DEVNULL)
    driver = webdriver.Firefox(options=opts, service=service)
    driver.implicitly_wait(4.0)

    yield driver

    driver.quit()
