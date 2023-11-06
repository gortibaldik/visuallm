from typing import Any

from visuallm.component_base import ComponentBase
from visuallm.elements.element_base import ElementBase, ElementWithEndpoint
from visuallm.elements.utils import register_named
from visuallm.named import NamedWrapper
from visuallm.server import Server


class CollapsibleElement(ElementWithEndpoint):
    def __init__(
        self,
        name: str = "collapsible-subcomponent",
        title="COLLAPSIBLE TITLE",
        subelements: list[ElementBase] | None = None,
    ):
        super().__init__(
            name=name, type="collapsible-subcomponent", endpoint_url="dummy"
        )
        self._title = title
        self.subelements: list[ElementBase] = []
        self.registered_subelement_names = set()

        if subelements is not None:
            for e in subelements:
                self.add_subelement(e)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        if value != self._title:
            self.set_changed()
        self._title = value

    def add_subelement(self, subelement: ElementBase):
        if subelement.is_registered_to_component:
            raise RuntimeError(
                "The subelement should be registered to subcomponent and"
                " the subcomponent will register it to the component"
            )
        if self.is_registered_to_component:
            raise RuntimeError(
                "Cannot add any subelement to a collapsible element"
                " after the collapsible element is already registered to a"
                " component"
            )
        subelement.set_name(f"{self.name}>>{subelement.name}")
        if subelement._order is None:
            if len(self.subelements) == 0:
                subelement.order = 1
            else:
                subelement.order = 1 + max(e.order for e in self.subelements)
        register_named(
            subelement,
            self.registered_subelement_names,
            self.subelements,
        )
        subelement.on_element_changed_callback = self._on_subelement_changed

    def _on_subelement_changed(self):
        self.set_changed()

    def register_to_component(self, component: ComponentBase):
        ElementBase.register_to_component(self, component)
        # subelement shouldn't be stored in the component, therefore
        # only the clashes in "endpoint_url" are checked
        for subelement in self.subelements:
            if not isinstance(subelement, ElementWithEndpoint):
                continue
            register_named(
                NamedWrapper(subelement, "endpoint_url"),
                component.registered_url_endpoints,
            )
            subelement._parent_component = component

    def register_to_server(self, server: Server):
        for subelement in self.subelements:
            if not isinstance(subelement, ElementWithEndpoint):
                continue
            subelement.register_to_server(server)

    def construct_element_configuration(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subelements": [
                subelement.construct_element_description()
                for subelement in sorted(self.subelements, key=lambda e: e.order)
            ],
        }

    def endpoint_callback(self):
        pass
