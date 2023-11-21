import multiprocessing
import time
from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

import pytest

from examples_py.persona_chat_example.create_app import create_app
from tests.example_modules_app_tests.conftest import app_run
from tests.port_utils import get_unused_port
from tests.stubs.generator_stub import EXCEPTION_MESSAGE, GeneratorStub

APP_PORT: int | None = None


@pytest.fixture(autouse=True)
def port():
    global APP_PORT
    return APP_PORT


def get_persona_traits():
    return [f"trait_{i}" for i in range(250)]


class TestSample(TypedDict):
    text: str
    target: str
    history: list[str]
    candidates: list[str]
    personality: list[str]


@pytest.fixture()
def exception_message():
    return EXCEPTION_MESSAGE


_history = [f"history{i}" for i in range(4)]
_candidates = ["history4"]
_personality = [f"personality{i}" for i in range(4)]
_datasets_data: dict[str, dict[str, Sequence[dict[str, Any]]]] = {
    f"dataset_{dix}": {  # type: ignore
        f"split_{dix}_{six}": [
            TestSample(  # type: ignore[misc]
                text=f"d{dix}_s{six}_text{tix}",
                target=f"s{six}target{tix}",
                history=_history,
                candidates=_candidates,
                personality=_personality,
            )
            for tix in range(20)
        ]
        for six in range(dix + 1)
    }
    for dix in range(3)
}


class Dataset:
    def __init__(self, name: str):
        self.name = name

    def __getitem__(self, selected_split: str) -> Sequence[dict[str, Any]]:
        if selected_split not in _datasets_data[self.name]:
            raise KeyError(f"{selected_split} not in dataset data!")
        return _datasets_data[self.name][selected_split]

    def keys(self):
        return _datasets_data[self.name].keys()


_datasets: Mapping[str, Dataset] = {
    f"dataset_{dix}": Dataset(f"dataset_{dix}") for dix in range(3)
}


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
        dataset=None,
        dataset_choices=_datasets,
        get_persona_traits=get_persona_traits,
        generator_choices={"generator1": GeneratorStub()},
        next_token_generator_choices={},
    )

    APP_PORT = get_unused_port()
    process = multiprocessing.Process(
        target=app_run, daemon=True, kwargs={"app": flask_app, "app_port": APP_PORT}
    )
    process.start()
    time.sleep(3.0)

    # by yielding None, fixture ensures that some result is returned from the
    # method but also ensures that some action can be taken after the end of the
    # test
    yield None

    process.terminate()


@pytest.fixture()
def full_app():
    global APP_PORT
    from examples_py.persona_chat_example.app import app

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
