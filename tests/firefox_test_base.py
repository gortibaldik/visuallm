from examples_py.app import app
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

class FlaskSeleniumFirefoxTestBase(LiveServerTestCase):

    def __init__(self, *args, address_suffix:str, **kwargs):
        self._address_suffix = address_suffix

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
        self.driver.get(self.get_server_url() + self._address_suffix)

    def tearDown(self):
        self.driver.quit()