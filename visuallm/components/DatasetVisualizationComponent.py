from typing import Optional

from visuallm.component_base import ComponentBase
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.elements.plain_text_element import PlainTextElement


class DatasetVisualization(ComponentBase, DataPreparationMixin):
    def __init__(
        self,
        title: str = "Dataset Visualization",
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
    ):
        self.main_heading_element = PlainTextElement(
            is_heading=True, heading_level=2, content=title
        )
        sample_vis_elements = self.initialize_sample_vis_elements()
        DataPreparationMixin.__init__(
            self,
            on_sample_change_callback=self.on_sample_change_callback,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )

        super().__init__(
            name="dataset_visualization",
            title=title,
            elements=[
                self.main_heading_element,
                *self.dataset_elements,
                *sample_vis_elements,
            ],
        )

    def initialize_sample_vis_elements(self):
        self.sample_vis_element = PlainTextElement()
        return [self.sample_vis_element]

    def update_sample_vis_elements(self):
        self.sample_vis_element.content = self._loaded_sample

    def on_sample_change_callback(self):
        self.update_sample_vis_elements()
