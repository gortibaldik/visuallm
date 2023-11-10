import multiprocessing
from collections.abc import Sequence
from typing import Any

import pytest

from examples_py.alpaca_example.create_app import create_app
from tests.example_modules_app_tests.conftest import app_run
from tests.port_utils import get_unused_port
from tests.stubs.generator_stub import GeneratorStub

_dataset_data = {
    f"split_{six}": [
        {"text": f"Some text {i}", "target": f"Some target {i}, {six}"}
        for i in range(10)
    ]
    for six in range(3)
}


class Dataset:
    def __getitem__(self, selected_split: str) -> Sequence[dict[str, Any]]:
        return _dataset_data[selected_split]

    def keys(self):
        return _dataset_data.keys()


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
    flask_app = create_app(
        dataset=Dataset(),  # type: ignore
        generator_choices={"generator1": GeneratorStub()},
        next_token_generator_choices={"generator1": GeneratorStub()},
    )

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
