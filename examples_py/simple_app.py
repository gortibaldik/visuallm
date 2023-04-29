from llm_generation_server.server import Server

from .simple_component import SimpleComponent

server = Server(__name__, [SimpleComponent()])
app = server.app
