from examples_py.dialogue_connections_example import ExampleDialogueConnectionsComponent
from examples_py.next_token_prediction_example import (
    ExampleNextTokenPredictionComponent,
)
from examples_py.really_easy_component_example import ReallyEasyComponent
from examples_py.sampling_example import ExampleSamplingComponent
from llm_generation_server.server import Server

next_token_component = ExampleNextTokenPredictionComponent()
connections_component = ExampleDialogueConnectionsComponent()
sampling_component = ExampleSamplingComponent()
really_easy_component = ReallyEasyComponent()


flask_app = Server(
    __name__,
    [
        next_token_component,
        connections_component,
        sampling_component,
        really_easy_component,
    ],
)
app = flask_app.app
