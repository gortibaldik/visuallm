import multiprocessing
import os

import pytest

from tests.example_modules_app_tests.conftest import app_run
from tests.port_utils import get_unused_port

APP_PORT: int | None = None


@pytest.fixture(autouse=True)
def port():
    global APP_PORT
    return APP_PORT


@pytest.fixture()
def full_app():
    global APP_PORT
    os.environ["OPENAI_API_KEY"] = "dumb"
    from examples_py.openai_example.app import app

    APP_PORT = get_unused_port()
    process = multiprocessing.Process(
        target=app_run, daemon=True, kwargs={"app": app, "app_port": APP_PORT}
    )
    process.start()

    # by yielding None, fixture ensures that some result is returned from the
    # method but also ensures that some action can be taken after the end of the
    # test
    yield None

    process.terminate()
