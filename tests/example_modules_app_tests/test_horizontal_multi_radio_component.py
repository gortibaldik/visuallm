import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/#/hmr_subcomponent"


def test_choices_work(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    hmr_element = firefox_driver.find_element(by=By.CLASS_NAME, value="hmr-wrapper")
    for i in range(5):
        input_radio = hmr_element.find_elements(by=By.TAG_NAME, value="input")
        input_radio[i].click()

        button = firefox_driver.find_element(by=By.TAG_NAME, value="button")
        button.click()

        text = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
        assert text.text == f"Last selected option: 'choice{i}'"
