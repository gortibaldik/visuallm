from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from visuallm.components.generators.base import Generator
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import ButtonElement, ChoicesSubElement

if TYPE_CHECKING:
    from visuallm.elements import ElementBase


GENERATOR_CHOICES = (
    dict[str, Generator]
    | dict[
        str,
        Callable[[], Generator],
    ]
)


class ModelSelectionMixin:
    def __init__(
        self,
        generator: Generator | None = None,
        generator_choices: GENERATOR_CHOICES | None = None,
        keep_generators_in_memory: bool = True,
    ):
        """Generator handling server methods. If only the
        generator is provided, the mixin just makes `self.generator` property available.
        If the `generator_choices` is available then the mixin creates frontend elements
        which let the user select the generator.

        Warning:
        -------
            You should either provide the generator or generator_choices,
            not both at once.

        Args:
        ----
            generator (Optional[Generator], optional): Implementation of the Generator class. Defaults to None.
            generator_choices (Optional[Generator], optional): dictionary where key
                is the name of the generator and value is the generator. Defaults to None.
            keep_generators_in_memory (bool, optional): Whether to load the tokenizer and model to cache, so that
                when a new tokenizer and model is loaded, the old one remains in memory. It makes switching
                between different tokenizers and models faster. Defaults to True.
        """
        if generator is None and (
            generator_choices is None or len(generator_choices) == 0
        ):
            raise ValueError(
                "You have to provide either generator or a not "
                "empty generator_choices dictionary"
            )

        if generator is None:
            self._generator_choices = generator_choices
        elif generator_choices is not None:
            raise ValueError(
                "If generator and generator_choices is all "
                "not None, the library cannot decide which should be "
                "selected."
            )
        else:
            self._generator_choices = None
            self._generator = generator

        self._cache: dict[str, Generator] | None = None
        if keep_generators_in_memory:
            self._cache = {}
        self.init_generator_selection_elements()

        if generator_choices is not None:
            self._generator = self.load_generator(
                generator_choices[self.generator_selector_element.value_on_backend]
            )

    def load_generator(
        self,
        generator_constructor: Generator
        | Callable[
            [],
            Generator,
        ],
    ):
        """Load the generator using the provided `generator_constructor`

        Args:
        ----
            generator_constructor (Union[Generator, Callable[[], Generator], ]): either
                the generator or a function that loads the generator.

        Returns:
        -------
            Generator
        """
        if isinstance(generator_constructor, Generator):
            return generator_constructor
        else:
            return generator_constructor()

    @property
    def generator(self):
        return self._generator

    def load_cached_generator(
        self,
        generator_constructor: Callable[[], Generator],
        name: str | None = None,
    ) -> None:
        """The behavior of this function depends on whether the caching is set or unset.

        If set, the function at first checks whether the generator with `name`
        is already in the cache and skips the loading and returns the cached value,
        or if it isn't then it loads the generator, and stores it into the cache and
        returns.

        If unset, the function just loads the generator and returns it.

        Important:
        ---------
            The loaded generator is stored in property `self.generator`

        Args:
        ----
            name (str): name of the tokenizer and the model, the tuple will be stored in the
                cache under this name.
            generator_constructor (Callable[[], Generator]): function that loads the generator.
        """
        if self._cache is not None and name in self._cache:
            self._generator = self._cache[name]
            return
        self._generator = generator_constructor()
        if self._cache is not None and name is not None:
            self._cache[name] = self._generator

    def init_generator_selection_elements(self):
        """Initializes a heading with text "Generator Settings" and a selector
        element, which contains:
        - selector for specific generator if multiple generators are provided
        """
        if self._generator_choices is None:
            return

        self.generator_selector_heading = PlainTextElement(
            content="Generator Settings", is_heading=True
        )
        self.generator_selector_element = ChoicesSubElement(
            list(self._generator_choices), text="Select Generator"
        )
        self.button_select_model = ButtonElement(
            processing_callback=self.on_generator_change_callback,
            button_text="Send Generator Configuration",
            subelements=[self.generator_selector_element],
        )

    @property
    def generator_selection_elements(self) -> list[ElementBase]:
        """All the generator selection elements that should be displayed on the frontend."""
        if self._generator_choices is None:
            return []
        return [self.generator_selector_heading, self.button_select_model]

    def after_on_generator_change_callback(self):
        """What to do after the new model and tokenizer is loaded."""
        pass

    def on_generator_change_callback(self):
        """Change the generator to another one based on a request from the frontend."""
        if self._generator_choices is None:
            return
        if self.generator_selector_element.updated:
            name = self.generator_selector_element.value_on_backend
            generator = self._generator_choices[name]
            self.load_cached_generator(lambda: self.load_generator(generator), name)
            self.after_on_generator_change_callback()
