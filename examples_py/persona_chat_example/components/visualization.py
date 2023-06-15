from visuallm.components.DatasetVisualizationComponent import DatasetVisualization

from .input_display import PersonaChatVisualization


class Visualization(DatasetVisualization, PersonaChatVisualization):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_sample_change_callback()

    def initialize_sample_vis_elements(self):
        return PersonaChatVisualization.init_model_input_display(self)

    def update_sample_vis_elements(self):
        PersonaChatVisualization.update_model_input_display(self)
