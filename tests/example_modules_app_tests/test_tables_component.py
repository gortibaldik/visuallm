import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


@pytest.fixture()
def link():
    return "http://127.0.0.1:5000/index.html#/table_component"


def test_table_is_present(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    elems = firefox_driver.find_elements(by=By.CLASS_NAME, value="spacedTables")

    assert len(elems) == 1

    table_elem = elems[0]
    tbody = table_elem.find_element(by=By.TAG_NAME, value="tbody")
    rows = tbody.find_elements(by=By.TAG_NAME, value="tr")
    row_values = [row.find_elements(by=By.TAG_NAME, value="td")[1].text for row in rows]

    expected_values = [
        f"This is {value} row"
        for value in ["first", "second", "third", "fourth", "fifth"]
    ]
    assert len(row_values) == len(expected_values)
    for expected, actual in zip(expected_values, row_values, strict=True):
        assert expected == actual


def test_connection_is_displayed(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    elems = firefox_driver.find_elements(by=By.CLASS_NAME, value="spacedTables")

    assert len(elems) == 1

    table_elem = elems[0]
    tbody = table_elem.find_element(by=By.TAG_NAME, value="tbody")
    rows = tbody.find_elements(by=By.TAG_NAME, value="tr")

    assert len(rows) == 5
    ActionChains(firefox_driver).move_to_element(rows[0]).perform()

    for row_index in range(1, 5):
        ActionChains(firefox_driver).move_to_element(rows[row_index]).perform()

        leader_line_elements = firefox_driver.find_elements(
            by=By.CLASS_NAME, value="leader-line"
        )
        expected_displayed = row_index
        actual_displayed = 0
        for leader_line_element in leader_line_elements:
            style = leader_line_element.value_of_css_property("visibility")
            if style == "visible":
                actual_displayed += 1

        assert expected_displayed == actual_displayed
