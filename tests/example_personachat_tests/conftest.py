import multiprocessing
from collections.abc import Sequence
from typing import Any, TypedDict

import pytest

from examples_py.persona_chat_example.create_app import create_app
from tests.example_modules_app_tests.conftest import app_run
from tests.port_utils import get_unused_port
from visuallm.components.generators.base import GeneratedOutput, Generator

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


EXCEPTION_MESSAGE = "RAISE EXCEPTION"


@pytest.fixture()
def exception_message():
    return EXCEPTION_MESSAGE


class GeneratorStub(Generator):

    """Dummy generator with few well defined options invoked through messages"""

    def create_text_to_tokenizer(
        self, loaded_sample: dict[str, Any], target: Any | None = None
    ) -> str:
        """The returned text is just the old text."""
        if not isinstance(loaded_sample, dict):
            raise TypeError()
        text = None
        if "text" in loaded_sample:
            text = loaded_sample["text"]
        elif "user_message" in loaded_sample:
            text = loaded_sample["user_message"]

        if text is None:
            raise TypeError()

        if text == EXCEPTION_MESSAGE:
            raise ValueError("Exception raised during generation!")

        return text

    def retrieve_target_str(self, loaded_sample: dict[str, Any]) -> str:
        if not isinstance(loaded_sample, dict):
            raise TypeError()
        if "target" not in loaded_sample:
            raise TypeError()

        return loaded_sample["target"]

    def generate_output(self, text_to_tokenizer: str, **kwargs):
        return GeneratedOutput(
            decoded_outputs=[f"generated text: '{text_to_tokenizer}'"]
        )


_history = [f"history{i}" for i in range(4)]
_candidates = ["history4"]
_personality = [f"personality{i}" for i in range(4)]
_dataset_data: dict[str, Sequence[dict[str, Any]]] = {  # type: ignore
    f"split_{six}": [
        TestSample(
            text="s{six}text{tix}",
            target="s{six}target{tix}",
            history=_history,
            candidates=_candidates,
            personality=_personality,
        )
        for tix in range(20)
    ]
    for six in range(5)
}


class Dataset:
    def __getitem__(self, selected_split: str) -> Sequence[dict[str, Any]]:
        if selected_split not in _dataset_data:
            raise KeyError(f"{selected_split} not in dataset data!")
        return _dataset_data[selected_split]

    def keys(self):
        return _dataset_data.keys()


# 35.59
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
        get_persona_traits=get_persona_traits,
        generator_choices={"generator1": GeneratorStub()},
        next_token_generator_choices={},
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
