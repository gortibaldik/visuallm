from __future__ import annotations

import secrets
import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable, MutableSet
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from visuallm.named import Named

from .element_base import ElementWithEndpoint
from .utils import assign_if_none, register_named


@dataclass
class SubElementConfiguration:
    subtype: str
    name: str
    configuration: dict[str, Any]
    parent_name: str


class ButtonElement(ElementWithEndpoint):

    """Frontend button element in a div with a list of subselectors.

    The list of subselectors may be empty, then only the button will appear.
    On the moment when user presses the button on the frontend, all the values
    from the subselectors are sent to the backend.

    Each subselector is automatically updated and contains at least 2 values
    stored in the following properties:
    - value_from_frontend: read-only, contains the value selected on the frontend
    - value_on_backend: read-write, contains exactly the same value as value_from_frontend
        but may be updated, and the updated value is sent back to the frontend (in case,
        when you want to change somehow the selected value and send it to user)

    After the user presses the button, and all the values of subselectors are updated,
    the user may work with the provided values by means of `processing_callback`. I.e.
    during the processing callback, the user has access to all the updated values.
    """

    def __init__(
        self,
        processing_callback: Callable[[], None],
        name: str = "button",
        subelements: list[SelectorSubElement] | None = None,
        button_text: str = "Select",
        disabled: bool = False,
        reload_page: bool = False,
        **kwargs,
    ):
        """Args:
        ----
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
            reload_page (bool): whether the whole page should be reloaded after
                the button is clicked
        """
        super().__init__(name=name, type="button", **kwargs)
        self.processing_callback = processing_callback
        self._button_text = button_text
        self._subelements_dict: dict[str, SelectorSubElement] = {}
        self._subelements: list[SelectorSubElement] = []
        self._subelement_names: MutableSet[str] = set()
        self._disabled = disabled
        self._reload_page = reload_page

        if subelements is None:
            subelements = []

        self.add_subelements(subelements)

    @property
    def subelements_iter(self):
        return iter(self._subelements)

    def set_subelements(self, subelements: list[SelectorSubElement]):
        """In case when you want to display only some of the subelements of the ButtonElement,
        you can set them here. However only the already added subelements can be set.
        """
        for s in subelements:
            if s.parent_element != self:
                raise RuntimeError(
                    "Only elements which have already been added to this element through"
                    " add_subelement, can be set."
                )

        self._subelements = subelements
        self.set_changed()

    @property
    def disabled(self):
        """Property controlling whether the button is clickable."""
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        if value != self._disabled:
            self.set_changed()
        self._disabled = value

    @property
    def button_text(self):
        return self._button_text

    @button_text.setter
    def button_text(self, value: str):
        if value != self._button_text:
            self.set_changed()
        self._button_text = value

    @property
    def reload_page(self):
        return self._reload_page

    def construct_element_configuration(self):
        subelement_configs = []
        for c in self._subelements:
            subelement_configs.append(c.subelement_configuration)
            c.unset_updated()
        return {
            "button_text": self.button_text,
            "disabled": self.disabled,
            "subelement_configs": subelement_configs,
            "reload_page": self.reload_page,
        }

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
            return self.parent_component.fetch_info(fetch_all=self.reload_page)
        except Exception:
            return self.parent_component.fetch_exception(traceback.format_exc())

    def add_subelement(self, subelement: SelectorSubElement):
        if subelement.parent_element is not None:
            raise RuntimeError()
        subelement.parent_element = self

        register_named(subelement, self._subelement_names, self._subelements)
        self._subelements_dict[subelement.name] = subelement

    def add_subelements(self, subelements: list[SelectorSubElement]):
        for s in subelements:
            self.add_subelement(s)


SelectedType = TypeVar("SelectedType")


class SelectorSubElement(ABC, Generic[SelectedType], Named):

    """Element that allows the user to select a value, and send it to backend with a button.

    Each SelectorSubElement serves for the user to select exactly one value. This value can
    be sent to the backend and be processed there. The value is stored in `value_from_frontend`
    property, and the processed value is saved in `value_on_backend` property. The processed
    value will be automatically sent to the frontend.
    """

    def __init__(
        self, subtype: str, text: str, default_value: SelectedType | None = None
    ):
        """Initialize SelectorSubElement, at the first moment of the server everything
        is new, so the `updated` property is set to `True`.

        Args:
        ----
            subtype (str): type which identifies the subelement in the frontend component
            text (str): text displayed to the left of the subelement (e.g. description of the
                action that is handled by the subelement)
            default_value (SelectedType): initial value of both `self.value_from_frontend` and
                `self.value_on_backend`
        """
        super().__init__(name=str(subtype))
        self._updated = True
        self._subtype = subtype
        self._value_from_frontend: SelectedType | None = default_value
        self._value_on_backend: SelectedType | None = default_value
        self.parent_element: ButtonElement | None = None
        self._text = text

    @property
    def subelement_configuration(self) -> SubElementConfiguration:
        if self.parent_element is None:
            raise RuntimeError()
        return SubElementConfiguration(
            self._subtype,
            self.name,
            {
                # TODO: rename selected on frontend
                "selected": self._value_on_backend,
                "text": self._text,
                **self.construct_subelement_specifics(),
            },
            self.parent_element.name,
        )

    @abstractmethod
    def construct_subelement_specifics(self) -> dict[str, Any]:
        """Return dict with all the values needed to instantiate the subelement
        in the frontend.
        """
        ...

    def _set_value_from_frontend(self, value: SelectedType):
        """Set value from frontend, value on backend and updated property"""
        if value != self._value_on_backend:
            self.force_set_updated()
        self._value_on_backend = value
        self._value_from_frontend = value

    @property
    @abstractmethod
    def value_from_frontend(self):
        """Value which arived from the frontend."""
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
        if self._value_from_frontend is None:
            raise ValueError("`self._value_from_frontend` not initialized yet!")
        return self._value_from_frontend

    def value_on_backend_getter(self) -> SelectedType:
        if self._value_on_backend is None:
            raise ValueError("`self._value_on_backend` not initialized yet!")
        return self._value_on_backend

    def value_on_backend_setter(self, value: SelectedType):
        if self.parent_element is None:
            raise ValueError(
                "Cannot change the value of the element without atributing "
                "the element to the parent component"
            )
        if value != self._value_on_backend:
            self.force_set_updated()
        self._value_on_backend = value

    def force_set_updated(self):
        """Set updated to true, so that any changes associated with the update
        are triggered
        """
        if self.parent_element is None:
            raise ValueError(
                "Cannot set the element to the updated state without "
                "atributing the element to the parent component"
            )
        self.parent_element.set_changed()
        self._updated = True

    def unset_updated(self):
        """Set updated to False."""
        self._updated = False

    @property
    def updated(self):
        """Whether the selector was updated by the frontend."""
        return self._updated


class MinMaxSubElement(SelectorSubElement[float]):

    """Select a number (possibly decimal), from a range [min, max]."""

    def __init__(
        self,
        sample_min: float,
        sample_max: float,
        text: str,
        step_size: float = 1.0,
        default_value: float | None = None,
    ):
        """Select a number (possibly decimal), from a range [min, max]

        Args:
        ----
            sample_min (float): minimum number that can be selected (inclusive)
            sample_max (float): maximum number that can be selected (inclusive)
            text (str): text that is displayed on the left of the selector
            step_size (float, optional): minimal difference between two adjacent values. Defaults to 1.0.
            default_value (Optional[float], optional): Default selected value, if None then sample_min is
                selected as default. Defaults to None.

        Raises:
        ------
            ValueError: if sample_min isn't smaller or equal to sample_max.
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
    def value_on_backend(self, value: float):
        if (value > self._max) or (value < self._min):
            raise ValueError(
                f"Invalid value ({value}) should be in range: ["
                f"{self._min}, {self._max}]"
            )
        self.value_on_backend_setter(value)

    def construct_subelement_specifics(self) -> dict[str, Any]:
        return {"min": self._min, "max": self._max, "step_size": self._step_size}


class ChoicesSubElement(SelectorSubElement[str]):
    def __init__(self, choices: list[str], text: str):
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

    def set_choices(self, new_choices: list[str]):
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

    def construct_subelement_specifics(self) -> dict[str, Any]:
        return {"choices": self._choices}

    def __len__(self):
        return len(self._choices)


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
            raise TypeError(f"Invalid value assigned to bool: {value}")
        self.value_on_backend_setter(value)

    def construct_subelement_specifics(self) -> dict[str, Any]:
        return {}


class TextInputSubElement(SelectorSubElement[str]):
    def __init__(
        self,
        placeholder_text: str = "Type something here",
        blank_after_text_send: bool = True,
        default_value: str = "",
    ):
        """Args:
        ----
            placeholder_text (str): Placeholder in the textarea. Defaults to "Type something here".
            blank_text_after_send (bool): Whether the text displayed in the text area should be blank after
                sending to the backend. Defaults to True.
            default_value (str): if the default value is set to "" then `placeholder_text` would be displayed
                on the frontend, otherwise this default value would be displayed (not as placeholder but as a
                first class text)
        """
        super().__init__(subtype="text_input", text="", default_value=default_value)
        self._placeholder_text = placeholder_text
        self.blank_after_text_send = blank_after_text_send

    @property
    def value_from_frontend(self):
        return self.value_from_frontend_getter()

    def _set_value_from_frontend(self, value: str):
        if value != self._value_on_backend:
            self.force_set_updated()
        if self.blank_after_text_send:
            self._value_on_backend = ""
        else:
            self._value_on_backend = value
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

    # TODO: make force set updated on change a decorator
    @placeholder_text.setter
    def placeholder_text(self, value: str):
        if value != self._placeholder_text:
            self.force_set_updated()
        self._placeholder_text = value

    def construct_subelement_specifics(self) -> dict[str, Any]:
        return {
            "placeholder_text": self.placeholder_text,
            "blank_after_text_send": self.blank_after_text_send,
            "random_number": secrets.randbelow(int(1e7)),
        }


class MultiRadioSubElement(SelectorSubElement[str]):
    def __init__(self, choices: list[str], text: str, is_horizontal: bool = True):
        """Display a series of radio buttons, either in horizontal or vertical direction.

        Args:
        ----
            choices (list[str]): choices that will be displayed on the frontend each
                with a radio input before it
            text (str): query written just in front of the choices
            is_horizontal (bool, optional): whether the choices will be organized
                horizontally or vertically on the frontend. Defaults to True.
        """
        if len(choices) == 0:
            raise ValueError("choices cannot be an empty list.")
        super().__init__("multi-radio", text=text, default_value=choices[0])
        self._choices = choices
        self._is_horizontal = is_horizontal

    @property
    def choices(self) -> list[str]:
        return self._choices

    @choices.setter
    def choices(self, value: list[str]):
        if self._choices != value:
            self.force_set_updated()
        self._choices = value

    @property
    def value_from_frontend(self):
        return self.value_from_frontend_getter()

    @property
    def value_on_backend(self):
        return self.value_on_backend_getter()

    @value_on_backend.setter
    def value_on_backend(self, value: str):
        self.value_on_backend_setter(value)

    def construct_subelement_specifics(self) -> dict[str, Any]:
        return {"choices": self._choices, "is_horizontal": self._is_horizontal}
