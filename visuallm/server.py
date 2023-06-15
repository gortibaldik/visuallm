import os
import sys
from dataclasses import dataclass
from typing import Callable, List, Set

from flask import Flask, jsonify, redirect
from flask_cors import CORS

from .component_base import ComponentBase


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
        self.registered_urls: Set[str] = set(["/", "/fetch_components"])
        self.registered_component_names: Set[str] = set()
        for component in self.components:
            component.init_app(self)

        self.add_endpoint(
            "/", lambda: redirect("/index.html", code=302), methods=["GET"]
        )
        self.add_endpoint("/fetch_components", self.fetch_components, methods=["GET"])
        CORS(self.app, resources={r"/*": {"origins": "*"}})

        print(f"Server initialized with following endpoints: {self.registered_urls}")

    def fetch_components(self):
        paths = []
        for component in self.components:
            paths.append(
                ComponentInfo(
                    name=component.name,
                    title=component.title,
                    default_fetch_path=component.default_url.removeprefix("/"),
                )
            )
        return jsonify(dict(result="success", context=paths))

    def run(self, **kwargs):
        self.app.run(**kwargs)

    def add_endpoint(self, url_name: str, f: Callable, methods: List[str]):
        self.app.add_url_rule(
            rule=url_name, endpoint=url_name, view_func=f, methods=methods
        )

    def _retrieve_static_files_path(self):
        dirname = os.path.dirname(__file__)
        static_path = os.path.join(dirname, "dist")
        print(f"Serving static files from {static_path}", file=sys.stderr)
        return static_path
