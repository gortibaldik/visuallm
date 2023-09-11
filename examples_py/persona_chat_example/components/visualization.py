from visuallm import DatasetVisualizationComponent

from .input_display import PersonaChatVisualization


class Visualization(DatasetVisualizationComponent, PersonaChatVisualization):
    def __post_init__(self):
        self.on_sample_change_callback()

    def initialize_sample_vis_elements(self):
        return PersonaChatVisualization.init_model_input_display(self)

    def update_sample_vis_elements(self):
        PersonaChatVisualization.update_model_input_display(self)
