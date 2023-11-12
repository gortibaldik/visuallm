import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@pytest.fixture()
def link(port: int):
    return f"http://localhost:{port}/index.html#/chat_component"


def test_after_send_message_should_stay(app, firefox_driver: Firefox, link: str):
    firefox_driver.get(link)

    sent_message = "test message"
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    # type message
    elem.send_keys(sent_message)

    # send message
    elem.send_keys(Keys.ENTER)

    # the message should stay in the text box for it to be easily editable
    # by the user
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    message_in_the_textbox = elem.get_attribute("value")
    assert sent_message == message_in_the_textbox


def test_after_send_message_text_to_tokenizer_should_be_displayed(
    app, firefox_driver: Firefox, link: str
):
    firefox_driver.get(link)

    sent_message = "test message"
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    # type message
    elem.clear()
    elem.send_keys(sent_message)

    # send message
    elem.send_keys(Keys.ENTER)

    text_elems = firefox_driver.find_elements(By.CLASS_NAME, "plainText")
    assert text_elems[0].text == sent_message
    assert text_elems[1].text == f"generated text: '{sent_message}'"


def test_after_accept_generation_textarea_should_be_blanked(
    app, firefox_driver: Firefox, link: str
):
    firefox_driver.get(link)

    sent_message = "test message"
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    # type message
    elem.clear()
    elem.send_keys(sent_message)

    # send message
    elem.send_keys(Keys.ENTER)

    button_elem = firefox_driver.find_elements(By.TAG_NAME, "button")[-1]
    assert button_elem.text == "Accept Generation"

    button_elem.click()
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    expected_value = ""
    textarea_text = elem.get_attribute("value")

    assert textarea_text == expected_value


def test_after_accept_generation_table_should_be_extended(
    app, firefox_driver: Firefox, link: str
):
    firefox_driver.get(link)

    spaced_tables = firefox_driver.find_element(By.CLASS_NAME, "spacedTables")
    history_table = spaced_tables.find_elements(By.CLASS_NAME, "table-wrapper")[-1]
    rows = history_table.find_elements(By.TAG_NAME, "tr")
    cells = [[d.text for d in r.find_elements(By.TAG_NAME, "td")] for r in rows]

    assert ";".join(cells[-1]) == "Bot;generated text: 'test message'"
    assert ";".join(cells[-2]) == "You;test message"


def test_exception_raised(
    app, firefox_driver: Firefox, link: str, exception_message: str
):
    import time

    firefox_driver.get(link)

    sent_message = exception_message
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    # type message
    elem.clear()
    elem.send_keys(sent_message)

    # send message
    elem.send_keys(Keys.ENTER)

    # firefox_driver.switch_to.alert
    time.sleep(0.2)
    alert = firefox_driver.switch_to.alert

    assert "ValueError: Exception raised during generation!" in alert.text

    alert.accept()
    time.sleep(0.2)

    # the page should work as before
    sent_message = "test message"
    elem = firefox_driver.find_element(By.TAG_NAME, "textarea")
    # type message
    elem.clear()
    elem.send_keys(sent_message)

    # send message
    elem.send_keys(Keys.ENTER)
    time.sleep(0.2)

    text_elems = firefox_driver.find_elements(By.CLASS_NAME, "plainText")
    assert text_elems[0].text == sent_message
    assert text_elems[1].text == f"generated text: '{sent_message}'"


def test_change_traits_traits_changed_text_cleared(
    app, firefox_driver: Firefox, link: str
):
    firefox_driver.get(link)

    textarea = firefox_driver.find_element(By.TAG_NAME, "textarea")
    textarea.clear()
    textarea.send_keys("Some Message")
    textarea.send_keys(Keys.ENTER)

    # assert correct starting position
    table = firefox_driver.find_element(By.TAG_NAME, "table")
    tbody = table.find_element(By.TAG_NAME, "tbody")
    val = tbody.find_element(By.TAG_NAME, "td")
    assert val.text == "trait_0"

    wrapper = firefox_driver.find_elements(By.TAG_NAME, "form")[2]
    subselector_wrapper = wrapper.find_element(By.CLASS_NAME, "subSelectorsWrapper")
    selector = subselector_wrapper.find_element(By.CLASS_NAME, "multiselect")
    selector.click()
    ActionChains(firefox_driver).send_keys(Keys.DOWN).perform()
    ActionChains(firefox_driver).send_keys(Keys.ENTER).perform()

    button = wrapper.find_element(By.TAG_NAME, "button")

    assert button.text == "Update Bot's Characteristics"
    button.click()

    table = firefox_driver.find_element(By.TAG_NAME, "table")
    tbody = table.find_element(By.TAG_NAME, "tbody")
    val = tbody.find_element(By.TAG_NAME, "td")
    assert val.text == "trait_1"

    # assert text cleared
    textarea = firefox_driver.find_element(By.TAG_NAME, "textarea")
    assert textarea.get_attribute("value") == ""
