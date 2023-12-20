import subprocess
import tempfile
from pathlib import Path

import pytest
from selenium import webdriver


@pytest.fixture(scope="session")
def download_dir():
    return Path(tempfile.mkdtemp())


@pytest.fixture(scope="session")
def firefox_driver(download_dir):
    """Create a selenium webdriver with firefox
    and runs it for the duration of whole module, and closes it after
    the last test in the module

    Yields
    ------
        selenium.webdriver.Firefox
    """
    opts = webdriver.FirefoxOptions()
    opts.add_argument("--headless")

    opts.set_preference("browser.download.panel.shown", False)
    opts.set_preference("browser.helperApps.neverAsk.openFile", True)
    opts.set_preference("browser.helperApps.neverAsk.saveToDisk", True)
    opts.set_preference("browser.download.manager.showWhenStarting", False)
    opts.set_preference("browser.download.manager.focusWhenStarting", False)
    opts.set_preference("browser.download.folderList", 2)
    opts.set_preference("browser.download.useDownloadDir", True)
    opts.set_preference("browser.helperApps.alwaysAsk.force", False)
    opts.set_preference("browser.download.manager.closeWhenDone", True)
    opts.set_preference("browser.download.manager.showAlertOnComplete", False)
    opts.set_preference("browser.download.manager.useWindow", False)
    opts.set_preference(
        "services.sync.prefs.sync.browser.download.manager.showWhenStarting", False
    )
    opts.set_preference("pdfjs.disabled", True)
    opts.set_preference("browser.download.dir", str(download_dir))

    service = webdriver.FirefoxService(log_output=subprocess.DEVNULL)
    driver = webdriver.Firefox(options=opts, service=service)
    driver.implicitly_wait(4.0)

    yield driver

    driver.quit()
