from flask import Flask, redirect
from flask_cors import CORS
from typing import Callable, List
from llm_generation_server.component_base import ComponentBase
import os
import sys


class FlaskGenerationApp:
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
        CORS(self.app, resources={r'/*': {'origins': '*'}})

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
