from flask import Flask, redirect, jsonify
from flask_cors import CORS
from typing import Callable, List
from llm_generation_server.component_base import ComponentBase
import os
import sys
from dataclasses import dataclass

@dataclass
class ComponentInfo:
    name: str
    title: str


class Server:
    def __init__(self, name, components: List[ComponentBase]):
        self.app = Flask(
            name,
            static_url_path="",
            static_folder=self._retrieve_static_files_path(),
            )
        
        self.components: List[ComponentBase] = components
        for component in self.components:
            component.init_app(self)
        self.add_endpoint(
            "/",
            lambda: redirect("/index.html", code=302),
            methods=['GET']
        )
        self.add_endpoint(
            "/fetch_components",
            self.fetch_components,
            methods=['GET']
        )
        CORS(self.app, resources={r'/*': {'origins': '*'}})

    def fetch_components(self):
        paths = []
        for component in self.components:
            paths.append(ComponentInfo(
                name=component.name,
                title=component.title
            ))
        return jsonify(dict(
            result="success",
            context=paths
        ))

    def run(self):
        self.app.run()
    
    def add_endpoint(
        self,
        url_name: str,
        f: Callable,
        methods: List[str],
    ):
        self.app.add_url_rule(
            rule=url_name,
            endpoint=None,
            view_func=f,
            methods=methods
        )
    
    def _retrieve_static_files_path(self):
        dirname = os.path.dirname(__file__)
        static_path = os.path.join(dirname, "dist")
        print(f"Serving static files from {static_path}", file=sys.stderr)
        return static_path
