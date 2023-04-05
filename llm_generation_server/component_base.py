from typing import Protocol

class ComponentBase(Protocol):
    def init_app(self, app):
        ...

    @property
    def name(self) -> str:
        ...
    
    @property
    def title(self) -> str:
        ...
