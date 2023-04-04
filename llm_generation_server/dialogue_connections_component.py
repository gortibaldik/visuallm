from llm_generation_server.server import Server
from abc import ABC, abstractmethod

class DialogueConnectionsComponent(ABC):
    def init_app(self, app: Server):
        self.app = app
        self.app.add_endpoint(
            "/fetch_connections",
            self.fetch_dialogue_connections,
            methods=['GET']
        )
    
    @abstractmethod
    def fetch_dialogue_connections(self):
        ...
