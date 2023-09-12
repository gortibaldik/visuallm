import unittest
import urllib3
from examples_py.app import app
from flask import Flask
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class FlaskSeleniumFirefoxTestBase(LiveServerTestCase):

    def create_app(self):
        app.config['LIVESERVER_PORT'] = 5000
        # Default timeout is 5 seconds
        app.config['LIVESERVER_TIMEOUT'] = 10
        return app

    def setUp(self):
        opts = FirefoxOptions()
        opts.add_argument('--headless')
        self.driver = webdriver.Firefox(options=opts)
        self.driver.implicitly_wait(2)
        self.driver.get(self.get_server_url() + "/index.html#/text_input_component")

    def tearDown(self):
        self.driver.quit()


class TextInputComponent_InsertTextInTextarea(FlaskSeleniumFirefoxTestBase):

    def test_insert_text_in_textarea(self):
        driver = self.driver
        test_text_value = "Some short text."
        elem = driver.find_element(By.TAG_NAME, "textarea")
        elem.send_keys(test_text_value)
        self.assertEqual(test_text_value, elem.get_attribute("value"))

    def test_textarea_cleared_after_form_submission(self):
        driver = self.driver
        test_text_value = "Some short text."
        form = driver.find_element(By.TAG_NAME, "form")
        textarea = form.find_element(By.TAG_NAME, "textarea")
        textarea.send_keys(test_text_value)
        button = form.find_element(By.TAG_NAME, "button")
        button.click()
        self.assertEqual(textarea.get_attribute("value"), "")

    def test_text_shown_in_wrap_element_after_form_submission(self):
        driver = self.driver
        test_text_value = "Some short text."
        form = driver.find_element(By.TAG_NAME, "form")
        textarea = form.find_element(By.TAG_NAME, "textarea")
        textarea.send_keys(test_text_value)
        button = form.find_element(By.TAG_NAME, "button")
        button.click()
        wrap_elem = driver.find_element(By.CLASS_NAME, "wrapElement")
        self.assertEqual(wrap_elem.text, test_text_value)

    def test_form_submitted_by_Enter_when_textarea_focused(self):
        driver = self.driver
        

    def test_form_submitted_by_Enter_when_submit_button_focused(self):
        driver = self.driver

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()