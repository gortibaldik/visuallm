from llm_generation_server.server import Server
from examples_py.next_token_prediction_example import ExampleNextTokenPredictionComponent
from examples_py.dialogue_connections_example import ExampleDialogueConnectionsComponent

next_token_component = ExampleNextTokenPredictionComponent()
next_token_component.initialize_vocab()
connections_component = ExampleDialogueConnectionsComponent()
flask_app = Server(__name__, [next_token_component, connections_component])
app = flask_app.app
