import multiprocessing

import flask
import pytest

from examples_py.example_modules.app import create_app
from tests.port_utils import get_unused_port

APP_PORT: int | None = None


def app_run(app: flask.app.Flask, app_port: int):
    print(f"RUNNING ON PORT {app_port}")
    app.run(debug=True, use_reloader=False, host="localhost", port=app_port)


@pytest.fixture()
def port():
    global APP_PORT
    return APP_PORT


@pytest.fixture(scope="session")
def app():
    """Fixture that creates and runs the flask application.
    Beware, this fixture is held during the whole lifetime of tests in a single
    module. Hence this may cause that single test failure may affect the results
    of other tests. However it has a performance benefit of not recreating a new
    flask application server for each test.

    After the last test all the resources associated with the app are closed.

    Yields
    ------
        app: process in which the Flask application is running
    """
    global APP_PORT

    flask_app = create_app()
    APP_PORT = get_unused_port()
    process = multiprocessing.Process(
        target=app_run, daemon=True, kwargs={"app": flask_app, "app_port": APP_PORT}
    )
    process.start()

    # by yielding None, fixture ensures that some result is returned from the
    # method but also ensures that some action can be taken after the end of the
    # test
    yield None

    process.terminate()
