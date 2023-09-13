from visuallm import DatasetVisualizationComponent

from .input_display import PersonaChatVisualization


class Visualization(DatasetVisualizationComponent, PersonaChatVisualization):
    def __post_init__(self):
        self.after_on_dataset_change_callback()

    def initialize_sample_visualization_elements(self):
        return [
            *PersonaChatVisualization.init_dialogue_vis_elements(self),
            *super().initialize_sample_visualization_elements(),
        ]

    def update_sample_vis_elements(self):
        self.text_to_tokenizer_element.content = (
            self.generator.create_text_to_tokenizer(
                self.loaded_sample, target=self.loaded_sample["candidates"][-1]
            )
        )
        PersonaChatVisualization.update_dialogue_structure_display(self)
