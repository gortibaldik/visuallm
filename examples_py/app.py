from llm_generation_server.server import Server

from .dialogue_connections_example import ExampleDialogueConnectionsComponent
from .next_token_prediction_example import ExampleNextTokenPredictionComponent
from .sampling_example import ExampleSamplingComponent
from .selector_component import SelectorComponent
from .table_component import TableComponent

flask_app = Server(
    __name__,
    [
        TableComponent(),
        SelectorComponent(),
        ExampleSamplingComponent(),
        ExampleDialogueConnectionsComponent(),
        ExampleNextTokenPredictionComponent(),
    ],
)
app = flask_app.app
