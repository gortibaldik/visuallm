from llm_generation_server.server_baseclass import FlaskGenerationApp
from llm_generation_server.ntpc_example import ExampleNextTokenPredictionComponent

next_token_component = ExampleNextTokenPredictionComponent()
flask_app = FlaskGenerationApp(__name__, [next_token_component])
next_token_component.initialize_context("Some initial context")
next_token_component.initialize_vocab()
app = flask_app.app