import multiprocessing

import flask
import pytest

from examples_py.example_modules.app import create_app


def app_run(app: flask.app.Flask):
    app.run(debug=True, use_reloader=False, host="localhost", port=5000)


@pytest.fixture(scope="module")
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
    flask_app = create_app()

    process = multiprocessing.Process(
        target=app_run, daemon=True, kwargs={"app": flask_app}
    )
    process.start()

    # by yielding None, fixture ensures that some result is returned from the
    # method but also ensures that some action can be taken after the end of the
    # test
    yield None

    process.terminate()
