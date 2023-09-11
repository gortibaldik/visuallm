from typing import List, Optional

from visuallm.component_base import ComponentBase, ComponentMetaclass
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.elements import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement


class DatasetVisualizationComponent(
    ComponentBase, DataPreparationMixin, metaclass=ComponentMetaclass
):
    def __init__(
        self,
        title: str = "Dataset Visualization",
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
    ):
        super().__init__(name="dataset_visualization", title=title)
        self.main_heading_element = PlainTextElement(
            is_heading=True, heading_level=2, content=title
        )
        sample_vis_elements = self.initialize_sample_vis_elements()
        DataPreparationMixin.__init__(
            self,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )

        self.add_element(self.main_heading_element)
        self.add_elements(self.dataset_elements)
        self.add_elements(sample_vis_elements)

    def initialize_sample_vis_elements(self) -> List[ElementBase]:
        self.sample_vis_element = PlainTextElement()
        return [self.sample_vis_element]

    def update_sample_vis_elements(self):
        self.sample_vis_element.content = self.loaded_sample

    def on_sample_change_callback(self):
        self.update_sample_vis_elements()
