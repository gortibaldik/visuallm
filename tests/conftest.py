import pytest
from selenium import webdriver


@pytest.fixture(scope="module")
def firefox_driver():
    """This is a fixture that creates a selenium webdriver with firefox
    and runs it for the duration of whole module, and closes it after
    the last test in the module

    Yields:
        selenium.webdriver.Firefox
    """
    opts = webdriver.FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    driver.implicitly_wait(2)

    yield driver

    driver.quit()
