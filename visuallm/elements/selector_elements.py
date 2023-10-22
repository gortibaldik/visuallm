from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, MutableSet, Optional, TypeVar

from visuallm.named import Named

from .element_base import ElementWithEndpoint
from .utils import assign_if_none, register_named


@dataclass
class SubElementConfiguration:
    subtype: str
    name: str
    configuration: Dict[str, Any]
    parent_name: str


class ButtonElement(ElementWithEndpoint):
    """I expect the following flow of data:
    - In frontend the user selects some value from the selector (automatic)
    - In frontend the user clicks the button element which is the parent of
        the selector (automatic)
    - The data arrives to backend, where each selector is updated and signalizes
        that is has been updated through `self.updated` flag (automatic)
    - the programmer can control what is influenced by updated selectors
    - all the changed elements are sent back to the frontend (automatic)
    """

    def __init__(
        self,
        processing_callback: Callable[[], None],
        name: str = "button",
        subelements: List[SelectorSubElement] = [],
        button_text: str = "Select",
        disabled: bool = False,
        **kwargs,
    ):
        """
        Args:
            processing_callback (Callable[[], None]): a function that is
                called just after all the data from the frontend have been
                processed.
            name (str, optional): name of the element, doesn't have to be
                provided. Defaults to "selector".
            subelements (List[SelectorSubElement], optional): input
                subelements. E.g. if there is a checkbox on each press of a
                button, the checkbox value will be sent to the backend.
                Defaults to [].
            button_text (str, optional): Text displayed in a button input
                element. Defaults to "Select".
            disabled (bool): whether the button should be clickable
        """
        super().__init__(name=name, type="button", **kwargs)
        self.processing_callback = processing_callback
        self._button_text = button_text
        self._subelements_dict: Dict[str, SelectorSubElement] = {}
        self._subelements: List[SelectorSubElement] = []
        self._subelement_names: MutableSet[str] = set()
        self._disabled = disabled

        for subelement in subelements:
            self.add_subelement(subelement)

    @property
    def subelements_iter(self):
        return iter(self._subelements)

    @property
    def disabled(self):
        """Property controlling whether the button is clickable."""
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        if value != self._disabled:
            self._changed = True
        self._disabled = value

    @property
    def button_text(self):
        return self._button_text

    @button_text.setter
    def button_text(self, value: str):
        if value != self._button_text:
            self._changed = True
        self._button_text = value

    def construct_element_configuration(self):
        subelement_configs = []
        for c in self._subelements:
            subelement_configs.append(c.subelement_configuration)
            c.unset_updated()
        return dict(
            button_text=self.button_text,
            disabled=self.disabled,
            subelement_configs=subelement_configs,
        )

    def _set_value_on_frontend_on_subelement(
        self, subelement: SelectorSubElement, value: Any
    ):
        if subelement.parent_element != self:
            raise ValueError("Updating subelement.selected on wrong subelement!")

        subelement._set_value_from_frontend(value)

    def endpoint_callback(self):
        """Goes over the standard format of response from FE and sets all
        the relevant selected attributes in subelement selectors, then returns
        the control to the programmer for handling of the updated data and
        then returns everything updated to the frontend.
        """
        try:
            response_json = self.get_request_dict()
            for key, value in response_json.items():
                self._set_value_on_frontend_on_subelement(
                    self._subelements_dict[key], value
                )

            self.processing_callback()
            return self.parent_component.fetch_info(fetch_all=False)
        except Exception:
            return self.parent_component.fetch_exception(traceback.format_exc())

    def add_subelement(self, subelement: SelectorSubElement):
        if subelement.parent_element is not None:
            raise RuntimeError()
        subelement.parent_element = self

        register_named(subelement, self._subelement_names, self._subelements)
        self._subelements_dict[subelement.name] = subelement


SelectedType = TypeVar("SelectedType")


class SelectorSubElement(ABC, Generic[SelectedType], Named):
    """I expect the following flow of data:
    - In frontend the user selects some value from the selector (automatic)
    - In frontend the user clicks the button element which is the parent of
        the selector (automatic)
    - The data arrives to backend, where each selector is updated and signalizes
        that is has been updated through `self.updated` flag (automatic)
    - the programmer can control what is influenced by updated selectors
    - all the changed elements are sent back to the frontend (automatic)
    """

    def __init__(
        self, subtype: str, text: str, default_value: Optional[SelectedType] = None
    ):
        """
        Initialize SelectorSubElement, at the first moment of the server everything
        is new, so the `updated` property is set to `True`.

        Args:
            subtype (str): type which identifies the subelement in the frontend component
            text (str): text displayed to the left of the subelement (e.g. description of the
                action that is handled by the subelement)
        """
        super().__init__(name=str(subtype))
        self._updated = True
        self._subtype = subtype
        self._value_from_frontend: Optional[SelectedType] = default_value
        self._value_on_backend: Optional[SelectedType] = default_value
        self.parent_element: Optional[ButtonElement] = None
        self._text = text

    @property
    def subelement_configuration(self) -> SubElementConfiguration:
        if self.parent_element is None:
            raise RuntimeError()
        return SubElementConfiguration(
            self._subtype,
            self.name,
            dict(
                # TODO: rename selected on frontend
                selected=self._value_on_backend,
                text=self._text,
                **self.construct_selector_data(),
            ),
            self.parent_element.name,
        )

    @abstractmethod
    def construct_selector_data(self) -> Dict[str, Any]:
        ...

    def _set_value_from_frontend(self, value: SelectedType):
        """Set value from frontend, value on backend and updated property"""
        if value != self._value_on_backend:
            self._updated = True
        self._value_on_backend = value
        self._value_from_frontend = value

    @property
    @abstractmethod
    def value_from_frontend(self):
        """
        Value which arived from the frontend.
        """
        ...

    @property
    @abstractmethod
    def value_on_backend(self):
        """Value, which will be sent to the frontend."""
        ...

    @value_on_backend.setter
    @abstractmethod
    def value_on_backend(self, value: SelectedType):
        ...

    def value_from_frontend_getter(self) -> SelectedType:
        assert self._value_from_frontend is not None
        return self._value_from_frontend

    def value_on_backend_getter(self) -> SelectedType:
        assert self._value_on_backend is not None
        return self._value_on_backend

    def value_on_backend_setter(self, value: SelectedType):
        if self.parent_element is None:
            raise ValueError(
                "Cannot change the value of the element without atributing "
                + "the element to the parent component"
            )
        if value != self._value_on_backend:
            self.force_set_updated()
        self._value_on_backend = value

    def force_set_updated(self):
        """Set updated to true, so that any changes associated with the update
        are triggered"""
        if self.parent_element is None:
            raise ValueError(
                "Cannot set the element to the updated state without "
                + "atributing the element to the parent component"
            )
        self.parent_element._changed = True
        self._updated = True

    def unset_updated(self):
        """Set updated to False."""
        self._updated = False

    @property
    def updated(self):
        """Whether the selector was updated by the frontend."""
        return self._updated


class MinMaxSubElement(SelectorSubElement[float]):
    """Subelement in the ButtonElement that creates an int selection in
    a range. E.g. selector between [min, max].
    """

    def __init__(
        self,
        sample_min: float,
        sample_max: float,
        text: str,
        step_size: float = 1.0,
        default_value: Optional[float] = None,
    ):
        """TODO

        Args:
            sample_min (float): _description_
            sample_max (float): _description_
            text (str): _description_
            step_size (float, optional): _description_. Defaults to 1.0.
            default_value (Optional[float], optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
        """
        super().__init__(
            subtype="min_max",
            text=text,
            default_value=assign_if_none(default_value, sample_min),
        )
        if sample_min > sample_max:
            raise ValueError(
                f"sample_min ({sample_min}) should be bigger than or equal "
                f"to sample_max ({sample_max})"
            )
        self._min = sample_min
        self._max = sample_max
        self._step_size = step_size

    @property
    def value_from_frontend(self) -> float:
        return self.value_from_frontend_getter()

    @property
    def value_on_backend(self):
        return self.value_on_backend_getter()

    @value_on_backend.setter
    def selected(self, value: float):
        if (value > self._max) or (value < self._min):
            raise ValueError(
                f"Invalid value ({value}) should be in range: ["
                + f"{self._min}, {self._max}]"
            )
        self.value_on_backend_setter(value)

    def construct_selector_data(self) -> Dict[str, Any]:
        return dict(min=self._min, max=self._max, step_size=self._step_size)


class ChoicesSubElement(SelectorSubElement[str]):
    def __init__(self, choices: List[str], text: str):
        """Default selected value is the first value in the `choices` list"""
        if len(choices) == 0:
            raise RuntimeError("choices should have length at least 1!")
        super().__init__(subtype="choices", text=text, default_value=choices[0])
        self._choices = choices

    @property
    def value_from_frontend(self):
        return self.value_from_frontend_getter()

    @property
    def value_on_backend(self):
        return self.value_on_backend_getter()

    @value_on_backend.setter
    def value_on_backend(self, value: str):
        if value not in self._choices:
            raise ValueError(f"Invalid value ({value}), possibilities: {self._choices}")
        self.value_on_backend_setter(value)

    def set_choices(self, new_choices: List[str]):
        """Update the value of the choices in the subelement. Updated
        choices must be a non-empty list. If the new choices don't contain
        the current `value_on_backend` then `value_on_backend` is updated.
        """
        if len(new_choices) == 0:
            raise RuntimeError("Choices should have length at least 1!")
        self._choices = new_choices
        if self._value_on_backend not in self._choices:
            self._value_on_backend = self._choices[0]
        self.force_set_updated()

    def construct_selector_data(self) -> Dict[str, Any]:
        return dict(choices=self._choices)


class CheckBoxSubElement(SelectorSubElement[bool]):
    def __init__(self, text: str, default_value: bool = False):
        super().__init__(subtype="check_box", text=text, default_value=default_value)

    @property
    def value_from_frontend(self):
        return self.value_from_frontend_getter()

    @property
    def value_on_backend(self):
        return self.value_on_backend_getter()

    @value_on_backend.setter
    def value_on_backend(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(f"Invalid value assigned to bool: {value}")
        self.value_on_backend_setter(value)

    def construct_selector_data(self) -> Dict[str, Any]:
        return {}


# what is different about text input element ?
# - it has a placeholder value
#


class TextInputElement(SelectorSubElement[str]):
    def __init__(self, placeholder_text: str, blank_after_text_send: bool = True):
        """
        Args:
            placeholder_text (str): Placeholder in the textarea. Defaults to "Type something here".
            blank_text_after_send (bool): Whether the text displayed in the text area should be blank after
                sending to the backend. Defaults to True.
        """
        super().__init__(subtype="text_input", text="", default_value="")
        self._placeholder_text = placeholder_text
        self.blank_after_text_send = blank_after_text_send

    @property
    def value_from_frontend(self):
        return self.value_from_frontend_getter()

    def _set_value_from_frontend(self, value: str):
        if value != self._value_on_backend:
            self._updated = True
        if self.blank_after_text_send:
            self._value_on_backend = ""
        self._value_from_frontend = value

    @property
    def value_on_backend(self):
        return self.value_on_backend_getter()

    @value_on_backend.setter
    def value_on_backend(self, value: str):
        self.value_on_backend_setter(value)

    @property
    def placeholder_text(self):
        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, value: str):
        if value != self._placeholder_text:
            self._updated = True
        self._placeholder_text = value

    @property
    def button_text(self) -> str:
        """Text that is displayed in the button on the side of the text box."""
        return self._button_text

    @button_text.setter
    def button_text(self, value: str) -> None:
        if value != self._button_text:
            self._changed = True
        self._button_text = value

    # def __init__(
    #     self,
    #     processing_callback: Callable[[], None],
    #     name: str = "text_input",
    #     button_text: str = "Send Text",
    #     default_text: str = "Type something here",
    #     blank_text_after_send: bool = True,
    # ):
    #     """Element with textarea input and a button with `button_text`.

    #     Args:
    #         processing_callback (Callable[[], None]): what to do after the user text input is sent
    #             to the backend
    #         name (str, optional): unique identifier of the element, if numerous elements share the same name, the library
    #             internally suffixes the names with suffixes so that the names of all the elements within one components
    #             are unique . Defaults to "text_input".
    #         button_text (str, optional): text to display on the button used to send the data. Defaults to "Send Text".
    #         default_text (str, optional): Placeholder in the textarea. Defaults to "Type something here".
    #         blank_text_after_send (bool, optional): Whether the text displayed in the text area should be blank after
    #             sending to the backend. Defaults to True.
    #     """
    #     super().__init__(name=name, type="text_input")
    #     self.processing_callback = processing_callback
    #     self._text_input = ""
    #     self._predefined_text_input = ""
    #     self._button_text = button_text
    #     self._default_text = default_text
    #     self._blank_text_after_send = blank_text_after_send

    # def endpoint_callback(self):
    #     response_json = self.get_request_dict()
    #     self._text_input = response_json["text_input"]
    #     if self._blank_text_after_send:
    #         self.predefined_text_input = ""
    #     else:
    #         self.predefined_text_input = self._text_input
    #     self.processing_callback()
    #     return self.parent_component.fetch_info(fetch_all=False)

    # @property
    # def text_input(self) -> str:
    #     """Data that is sent from the user."""
    #     return self._text_input

    # @property
    # def predefined_text_input(self) -> str:
    #     """Data that will be displayed to the user in the textarea of the element."""
    #     return self._predefined_text_input

    # @predefined_text_input.setter
    # def predefined_text_input(self, value: str) -> None:
    #     if value != self._predefined_text_input:
    #         self._changed = True
    #     self._predefined_text_input = value

    def construct_element_configuration(self):
        return dict(
            button_text=self.button_text,
            # TODO: rename default_text to placeholder
            default_text=self.placeholder_text,
            text_input=self.value_on_backend,
        )
