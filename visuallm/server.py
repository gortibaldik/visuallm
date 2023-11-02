from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from flask import Flask, redirect
from flask_cors import CORS

if TYPE_CHECKING:
    from .component_base import ComponentBase


@dataclass
class ComponentInfo:
    name: str
    title: str
    default_fetch_path: str


class Server:
    def __init__(self, name, components: list[ComponentBase]):
        self.app = Flask(
            name,
            static_url_path="",
            static_folder=self._retrieve_static_files_path(),
        )

        self.components: list[ComponentBase] = components
        self.registered_urls: set[str] = {"/", "/fetch_component_infos"}
        self.registered_component_names: set[str] = set()
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
        """Send to the FE which components will be parts of the app."""
        component_infos = []
        for component in self.components:
            component_infos.append(
                ComponentInfo(
                    name=component.name,
                    title=component.title,
                    default_fetch_path=component.default_url.removeprefix("/"),
                )
            )
        return {"result": "success", "component_infos": component_infos}

    def run(self, **kwargs):
        self.app.run(**kwargs)

    def add_endpoint(self, url_name: str, api_method: Callable, methods: list[str]):
        """Add API endpoint with name `url_name`, which will on invocation
        call method `api_method`. The `api_method` is invoked each time when
        the frontend makes request to `url_name` with any of specified
        `methods`, e.g. "GET", "POST" or others.

        Args:
        ----
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
        dirname = Path(__file__).parent
        static_path = dirname / "dist"
        print(f"Serving static files from {static_path}", file=sys.stderr)
        return static_path
