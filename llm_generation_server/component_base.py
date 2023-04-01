from typing import Protocol

class ComponentBase(Protocol):
    def init_app(self, app):
        ...
