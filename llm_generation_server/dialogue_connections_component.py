from llm_generation_server.server import Server
from flask import jsonify, request
from abc import ABC, abstractmethod

class DialogueConnectionsComponent(ABC):
    def init_app(self, app: Server):
        self.app = app
        self.app.add_endpoint(
            "/fetch_connections",
            self.fetch_dialogue_connections,
            methods=['GET']
        )
        self.app.add_endpoint(
            "/select_dataset_sample_links",
            self.select_dataset_sample_links,
            methods=['POST']
        )

    def select_dataset_sample_links(self):
        data = request.get_json()
        sample_n: int = data.get('sample_n')
        self.load_dataset_sample(sample_n)
        return self.fetch_dialogue_connections()
    
    @abstractmethod
    def load_dataset_sample(self, sample_n: int):
        ...

    @property
    def name(self):
        return "connections"
    
    @property
    def title(self):
        return "Table Connections"

    def fetch_dialogue_connections(self):
        return jsonify(dict(
            result="success",
            content=self.table_formatter.format(),
            sample_selector=self.sample_selector_formatter.format()
        ))
