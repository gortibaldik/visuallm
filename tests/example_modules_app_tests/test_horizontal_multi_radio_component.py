import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/#/hmr_subcomponent"


def test_choices_1_reflect_in_plain_text_n_deselect_works(
    app, firefox_driver: Firefox, link: str
):
    firefox_driver.get(link)

    for i in range(5):
        hmr_element = firefox_driver.find_element(by=By.CLASS_NAME, value="hmr-wrapper")
        input_radios = hmr_element.find_elements(by=By.TAG_NAME, value="input")
        input_radios[i].click()

        button = firefox_driver.find_element(by=By.TAG_NAME, value="button")
        button.click()

        text = firefox_driver.find_element(by=By.CLASS_NAME, value="plainText")
        assert text.text == f"Last selected option: 'choice{i}'"

        # assert that nothing is selected anymore
        hmr_element = firefox_driver.find_element(by=By.CLASS_NAME, value="hmr-wrapper")
        input_radios = hmr_element.find_elements(by=By.TAG_NAME, value="input")
        for j in range(5):
            assert not input_radios[j].is_selected()


def test_choices_2_reflect_in_plain_text(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    for i in range(5):
        hmr_element = firefox_driver.find_elements(
            by=By.CLASS_NAME, value="hmr-wrapper"
        )[1]
        input_radios = hmr_element.find_elements(by=By.TAG_NAME, value="input")
        input_radios[i].click()

        button = firefox_driver.find_elements(by=By.TAG_NAME, value="button")
        button[1].click()

        text = firefox_driver.find_elements(by=By.CLASS_NAME, value="plainText")[1]
        assert text.text == f"Last selected option: 'choice{i}'"

        hmr_element = firefox_driver.find_elements(
            by=By.CLASS_NAME, value="hmr-wrapper"
        )[1]
        # assert that nothing is selected anymore
        input_radios = hmr_element.find_elements(by=By.TAG_NAME, value="input")
        for j in range(5):
            assert input_radios[j].is_selected() == (i == j)
