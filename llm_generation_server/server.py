from flask import Flask, redirect, jsonify
from flask_cors import CORS
from typing import Callable, List, Set
from llm_generation_server.component_base import ComponentBase
import os
import sys
from dataclasses import dataclass

@dataclass
class ComponentInfo:
    name: str
    title: str
    default_fetch_path: str


class Server:
    def __init__(self, name, components: List[ComponentBase]):
        self.app = Flask(
            name,
            static_url_path="",
            static_folder=self._retrieve_static_files_path(),
            )
        
        self.components: List[ComponentBase] = components
        self.registered_default_urls: Set[str] = set()
        for component in self.components:
            component.init_app(self)
            if component.default_url in self.registered_default_urls:
                raise ValueError(f"{component.default_url} in two different components!")
            self.registered_default_urls.add(component.default_url)

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
                title=component.title,
                default_fetch_path=component.default_url
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
        methods: List[str]
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
