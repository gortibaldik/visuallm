from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datasets import DatasetDict  # type: ignore[import]

from visuallm import (
    DatasetVisualizationComponent,
    GenerationComponent,
    NextTokenPredictionComponent,
)
from visuallm.components.generators.base import Generator
from visuallm.server import Server


def create_app(
    dataset: "DatasetDict",
    generator_choices: dict[str, Generator],
    next_token_generator_choices: dict[str, Generator] | None = None,
):
    visualize = DatasetVisualizationComponent(
        generator_choices=generator_choices, dataset=dataset
    )
    generate = GenerationComponent(generator_choices=generator_choices, dataset=dataset)
    components = [visualize, generate]
    if next_token_generator_choices is not None:
        next_token = NextTokenPredictionComponent(
            generator_choices=generator_choices, dataset=dataset
        )
        components.append(next_token)

    server = Server(__name__, components)
    app = server.app

    return app
