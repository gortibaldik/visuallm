from llm_generation_server.server_exampleclass import FlaskGenerationExampleApp

baseclass = FlaskGenerationExampleApp(__name__)
baseclass.initialize_context("Some initial context")
baseclass.initialize_vocab()
app = baseclass.app