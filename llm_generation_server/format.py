from dataclasses import dataclass
from enum import Enum
from typing import Dict, Protocol

@dataclass
class FormattedContext:
    type: str
    content: Dict

class Formatter(Protocol):
    def format():
        pass