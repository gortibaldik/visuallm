from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from visuallm.component_base import ComponentBase
from visuallm.elements.element_base import ElementBase, ElementWithEndpoint
from visuallm.elements.utils import register_named
from visuallm.named import NamedWrapper
from visuallm.server import Server


class CollapsibleElement(ElementWithEndpoint):
    def __init__(
        self,
        name: str = "collapsible-element",
        title: str = "COLLAPSIBLE TITLE",
        subelements: list[ElementBase] | None = None,
        is_collapsed: bool = True,
    ):
        """Element that serves as a parent element of its child subelements. On the frontend it is displayed as a button
        with text `title` that after click expands and shows all the other child subelements.

        This class is an instance of ElementWithEndpoint so that all the endpoints of the subelements could be added
        to the server. However it doesn't have any API endpoint itself.

        Args:
        ----
            name (str): name of the element, unique identifier of the element
                in the component. If you name multiple components the same, the library appends number after the element.
            title (str, optional): Title that is displayed on the button that expands the collapsible. Defaults to "COLLAPSIBLE TITLE".
                (dummy default should notify you on the page that it should be updated)
            subelements (list[ElementBase] | None, optional): Subelements that will be displayed in the expanded section of the
                collapsible. Defaults to None.
            is_collapsed (bool, optional): Whether by default (on page load), this element is in collapsed or expanded state.
        """
        super().__init__(name=name, type="collapsible-element", endpoint_url="dummy")
        self._title = title
        self._is_collapsed = is_collapsed
        self.subelements: list[ElementBase] = []
        self.registered_subelement_names: set[str] = set()

        if subelements is not None:
            self.add_subelements(subelements)

    @property
    def is_collapsed(self):
        """Whether by default (on page load), this element is in collapsed or expanded state."""
        return self._is_collapsed

    @is_collapsed.setter
    def is_collapsed(self, value: bool):
        if value != self._is_collapsed:
            self.set_changed()
        self._is_collapsed = value

    @property
    def title(self):
        """Title that is displayed on the button which expands the collapsible."""
        return self._title

    @title.setter
    def title(self, value: str):
        if value != self._title:
            self.set_changed()
        self._title = value

    def add_subelements(self, subelements: list[ElementBase], order: int | None = None):
        """Add subelements. Each ElementBase can be a subelement of at most one element.
        Each added subelement will have the same order.

        Args:
        ----
            subelements (ElementBase): elements that will be displayed in the expandable
                section of this element on the frontend
            order (int, optional): order in which the elements occurs in the collapsible,
                lower value means higher position on the page
        """
        for e in subelements:
            self.add_subelement(e, order=order)

    def add_subelement(self, subelement: ElementBase, order: int | None = None):
        """Add subelement. Each ElementBase can be a subelement of at most one element.

        Args:
        ----
            subelement (ElementBase): element that will be displayed in the expandable
                section of this element on the frontend
            order (int, optional): order in which the element occurs in the collapsible,
                lower value means higher position on the page
        """
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
        if order is not None and order <= 0:
            raise ValueError(f"Order should be positive (current value: {order})")
        if order is None:
            if len(self.subelements) == 0:
                subelement.order = 1
            else:
                subelement.order = 1 + max(e.order for e in self.subelements)
        else:
            subelement.order = order
        register_named(
            subelement,
            self.registered_subelement_names,
            self.subelements,
        )
        subelement.on_element_changed_callback = self._on_subelement_changed

    def _on_subelement_changed(self):
        self.set_changed()

    def register_to_component(self, component: "ComponentBase"):
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
        subelements: list[dict[str, Any]] = []
        for subelement in sorted(self.subelements, key=lambda e: e.order):
            descr = subelement.construct_element_description()
            descr["name"] = self.name + ">>" + descr["name"]
            if "subelement_configs" not in descr:
                subelements.append(descr)
                continue
            for config in descr["subelement_configs"]:
                config.parent_name = descr["name"]
            subelements.append(descr)
        return {
            "title": self.title,
            "is_collapsed": self.is_collapsed,
            "subelements": subelements,
        }

    def endpoint_callback(self):
        pass
