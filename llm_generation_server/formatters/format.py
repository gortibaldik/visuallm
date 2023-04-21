from dataclasses import dataclass
from typing import Dict
from abc import ABC, abstractmethod


@dataclass
class FormattedContext:
    name: str
    type: str
    content: Dict


class Formatter(ABC):
    def __init__(self, name: str):
        self.name = name
        self.changed = True

    @abstractmethod
    def format(self):
        ...

    @abstractmethod
    def add_endpoint(self, app):
        ...
