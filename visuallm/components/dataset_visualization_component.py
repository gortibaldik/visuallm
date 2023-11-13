import logging

from visuallm.component_base import ComponentBase
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.components.mixins.model_selection_mixin import (
    GENERATOR_CHOICES,
    Generator,
    ModelSelectionMixin,
)
from visuallm.elements import ElementBase, HeadingElement, PlainTextElement


class DatasetVisualizationComponent(
    ComponentBase, DataPreparationMixin, ModelSelectionMixin
):
    def __init__(
        self,
        title: str = "Dataset Visualization",
        generator: Generator | None = None,
        generator_choices: GENERATOR_CHOICES | None = None,
        dataset: DATASET_TYPE | None = None,
        dataset_choices: DATASETS_TYPE | None = None,
    ):
        super().__init__(name="dataset_visualization", title=title)
        self.main_heading_element = PlainTextElement(
            is_heading=True, heading_level=2, content=title
        )
        sample_vis_elements = self.initialize_sample_visualization_elements()
        DataPreparationMixin.__init__(
            self,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )
        ModelSelectionMixin.__init__(
            self, generator=generator, generator_choices=generator_choices
        )

        self.add_element(self.main_heading_element)
        self.add_elements(self.dataset_choice_elements)
        self.add_elements(self.generator_selection_elements)
        self.add_elements(sample_vis_elements)

    def __post_init__(self, *args, **kwargs):
        self.update_sample_vis_elements()

    def initialize_sample_visualization_elements(self) -> list[ElementBase]:
        text_to_tokenizer_heading = HeadingElement(content="Text Model Inputs")
        self.text_to_tokenizer_element = PlainTextElement()

        expected_output_heading = HeadingElement(content="Expected Output")
        self.expected_output_element = PlainTextElement()
        return [
            text_to_tokenizer_heading,
            self.text_to_tokenizer_element,
            expected_output_heading,
            self.expected_output_element,
        ]

    def update_sample_vis_elements(self):
        if self.generator.create_text_to_tokenizer is None:
            raise CreateTextToTokenizerIsNoneError()
        self.text_to_tokenizer_element.content = (
            self.generator.create_text_to_tokenizer(self.loaded_sample)
        )
        if self.generator.retrieve_target_str is None:
            raise RetrieveTargetStrIsNoneError()
        self.expected_output_element.content = self.generator.retrieve_target_str(
            self.loaded_sample
        )

    def after_on_dataset_change_callback(self):
        self.update_sample_vis_elements()

    def after_on_generator_change_callback(self):
        self.update_sample_vis_elements()

    def _check_generators(
        self,
        generator: Generator | None,
        generator_choices: GENERATOR_CHOICES | None,
    ):
        if generator_choices is None:
            if generator is None:
                raise ValueError(
                    "Either generator_choices or generator should not be None"
                )
            generator_choices = {"default": generator}

        for _name, _generator in generator_choices.items():
            if callable(_generator):
                logging.info(f"Not checking generator '{_name}' because it is callable")
                continue

            if _generator.retrieve_target_str is None:
                raise RetrieveTargetStrIsNoneError()
            if _generator.create_text_to_tokenizer is None:
                raise CreateTextToTokenizerIsNoneError()


class CreateTextToTokenizerIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "self.generator.create_text_to_tokenizer is None, DatasetVisualizationComponent needs it!"
        )


class RetrieveTargetStrIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "self.generator.retrieve_target_str is None, DatasetVisualizationComponent needs it!"
        )
