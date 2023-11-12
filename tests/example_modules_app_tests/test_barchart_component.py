import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://127.0.0.1:{port}/index.html#/barchart_component"


def test_barchart_is_present(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    elems = firefox_driver.find_elements(by=By.CLASS_NAME, value="barChartSelect")

    assert len(elems) == 1

    bar_chart_elem = elems[0]
    progress_bar_elems = bar_chart_elem.find_elements(
        by=By.CLASS_NAME, value="progress-bar"
    )
    assert len(progress_bar_elems) == 10
    button_elems = bar_chart_elem.find_elements(by=By.CLASS_NAME, value="button")
    assert len(button_elems) == 1


def test_click_possibility_button_text_changes(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)
    bar_chart_elem = firefox_driver.find_element(
        by=By.CLASS_NAME, value="barChartSelect"
    )
    progress_bar_elems = bar_chart_elem.find_elements(
        by=By.CLASS_NAME, value="progress-bar"
    )

    for i in range(10):
        pb_elem = progress_bar_elems[i]
        input_radio_elem = pb_elem.find_element(by=By.CLASS_NAME, value="input-radio")
        value_of_input_radio = input_radio_elem.get_attribute("value")
        displayed_value = pb_elem.find_element(by=By.CLASS_NAME, value="word-text").text

        assert value_of_input_radio == displayed_value

        input_radio_elem.click()

        button_elem = bar_chart_elem.find_element(by=By.CLASS_NAME, value="button")
        assert f'Select "{displayed_value}"' == button_elem.text


def test_after_send_the_value_changes(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    for i in range(10):
        bar_chart_elem = firefox_driver.find_element(
            by=By.CLASS_NAME, value="barChartSelect"
        )
        progress_bar_elems = bar_chart_elem.find_elements(
            by=By.CLASS_NAME, value="progress-bar"
        )
        input_radio_elem = progress_bar_elems[i].find_element(
            by=By.CLASS_NAME, value="input-radio"
        )
        value_of_input_radio = input_radio_elem.get_attribute("value")
        input_radio_elem.click()

        button_elem = bar_chart_elem.find_element(by=By.CLASS_NAME, value="button")
        button_elem.click()

        time.sleep(0.05)
        display_elem = firefox_driver.find_elements(
            by=By.CLASS_NAME, value="plainText"
        )[-1]

        assert f"Last selected: {value_of_input_radio}" == display_elem.text
