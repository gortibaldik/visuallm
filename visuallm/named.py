from typing import Protocol


class Named:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def set_name(self, value: str):
        self._name = value


class NamedProtocol(Protocol):
    @property
    def name(self) -> str:
        ...

    def set_name(self, value: str):
        pass


class NamedWrapper:
    def __init__(self, internal_object, attr_name: str = "endpoint_url"):
        self.internal_object = internal_object
        self.attr_name = attr_name

    @property
    def name(self):
        return getattr(self.internal_object, self.attr_name)

    def set_name(self, value: str):
        setattr(self.internal_object, self.attr_name, value)
