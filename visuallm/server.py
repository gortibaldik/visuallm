from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, List, Set

from flask import Flask, jsonify, redirect
from flask_cors import CORS

if TYPE_CHECKING:
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
        self.registered_urls: Set[str] = set(["/", "/fetch_component_infos"])
        self.registered_component_names: Set[str] = set()
        for component in self.components:
            component.register_to_server(self)

        self.add_endpoint(
            "/", lambda: redirect("/index.html", code=302), methods=["GET"]
        )
        self.add_endpoint(
            "/fetch_component_infos", self.on_fetch_component_infos, methods=["GET"]
        )
        CORS(self.app, resources={r"/*": {"origins": "*"}})

        print(f"Server initialized with following endpoints: {self.registered_urls}")

    def on_fetch_component_infos(self):
        """
        Callback that enables the frontend to create components (i.e. tabs in your application)
        """
        component_infos = []
        for component in self.components:
            component_infos.append(
                ComponentInfo(
                    name=component.name,
                    title=component.title,
                    default_fetch_path=component.default_url.removeprefix("/"),
                )
            )
        return jsonify(dict(result="success", component_infos=component_infos))

    def run(self, **kwargs):
        self.app.run(**kwargs)

    def add_endpoint(self, url_name: str, api_method: Callable, methods: List[str]):
        """Add API endpoint with name `url_name`, which will on invocation
        call method `api_method`. The `api_method` is invoked each time when
        the frontend makes request to `url_name` with any of specified
        `methods`, e.g. "GET", "POST" or others.

        Args:
            url_name (str): name of the endpoint
            api_method (Callable): method invoked when a request to `url_name`
                is made
            methods (List[str]): list of REST methods which is linked to
                the enpoint
        """
        self.app.add_url_rule(
            rule=url_name, endpoint=url_name, view_func=api_method, methods=methods
        )

    def _retrieve_static_files_path(self):
        dirname = os.path.dirname(__file__)
        static_path = os.path.join(dirname, "dist")
        print(f"Serving static files from {static_path}", file=sys.stderr)
        return static_path
