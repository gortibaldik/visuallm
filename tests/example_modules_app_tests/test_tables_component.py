import time
from pathlib import Path

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


@pytest.fixture()
def link(port: int):
    return f"http://127.0.0.1:{port}/index.html#/table_component"


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
    ] + [
        "This is row with <html> <tags>",
        "This is a multi line\nrow so it should be\ndisplayed on multiple lines.",
        "Another Row just because",
        "And another one",
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

    expected_rows = 9
    assert len(rows) == expected_rows
    ActionChains(firefox_driver).move_to_element(rows[0]).perform()

    for row_index in range(1, expected_rows):
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


def test_copy_works(app, firefox_driver: Firefox, link: str, download_dir: Path):
    firefox_driver.get(link)

    elems = firefox_driver.find_elements(by=By.CLASS_NAME, value="spacedTables")

    assert len(elems) == 1

    button = elems[0].find_element(By.CLASS_NAME, "download-button")
    assert button.text == "LaTEX"
    button.click()

    # wait for the modal to show
    time.sleep(0.2)

    modal_elem = firefox_driver.find_element(By.CLASS_NAME, "modal")
    text_elem = modal_elem.find_element(By.CLASS_NAME, "wrapElement")
    expected = r"""\begin{center}
\begin{tabular}{c c c c}
No. & Turn & Another & Column \\
\hline
0 & This is first row & Another-1. & Column-1. \\
1 & This is second row & Another-2. & Column-2. \\
2 & This is third row & Another-3. & Column-3. \\
3 & This is fourth row & Another-4. & Column-4. \\
4 & This is fifth row & Another-5. & Column-5. \\
5 & This is row with \texttt{<html>} \texttt{<tags>} & Another-6. & Column-6. \\
6 & \multirow{3}{*}{\parbox{14em}{\centering This is a multi line\\row so it should be\\displayed on multiple lines.}} & Another-7. & Column-7. \\
& & & \\
& & & \\
7 & Another Row just because & Another-8. & Column-8. \\
8 & And another one & Another-9. & Column-9.
\end{tabular}
\end{center}"""
    expected2 = r"""\begin{center}
\begin{tabular}{c c c c}
No. & Turn & Another & Column \\
\hline
0 & This is first row & Another-1. & Column-1. \\
1 & This is second row & Another-2. & Column-2. \\
2 & This is third row & Another-3. & Column-3. \\
3 & This is fourth row & Another-4. & Column-4. \\
4 & This is fifth row & Another-5. & Column-5. \\
5 & This is row with \texttt{<html>} \texttt{<tags>} & Another-6. & Column-6. \\
6 & \multirow{3}{*}{\parbox{14em}{\centering This is a multi line\\row so it should be\\displayed on multiple lines.}} & Another-7. & Column-7. \\
 &  &  &  \\
 &  &  &  \\
7 & Another Row just because & Another-8. & Column-8. \\
8 & And another one & Another-9. & Column-9.
\end{tabular}
\end{center}""".replace(
        "\n", ""
    )

    assert text_elem.text == expected

    buttons = modal_elem.find_elements(By.TAG_NAME, "button")
    assert len(buttons) == 2
    assert buttons[0].text == "Close"
    assert buttons[1].text == "Copy"

    buttons[1].click()
    elems = modal_elem.find_elements(By.CLASS_NAME, "copy-message")
    assert len(elems) == 1
    assert elems[0].text == "Copied!"

    time.sleep(0.2)
    textarea = modal_elem.find_element(By.TAG_NAME, "input")
    assert textarea.get_attribute("value") == expected2

    buttons[0].click()
    time.sleep(0.2)

    modal_elems = firefox_driver.find_elements(By.CLASS_NAME, "modal")
    assert len(modal_elems) == 0
