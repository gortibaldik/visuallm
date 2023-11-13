from visuallm.components import NextTokenPredictionComponent

from .input_display import PersonaChatVisualization


class NextTokenPrediction(NextTokenPredictionComponent, PersonaChatVisualization):
    def __post_init__(self, *args, **kwargs):
        self.after_on_generator_change_callback()

    def init_model_input_display_elements(self):
        return [
            *PersonaChatVisualization.init_dialogue_vis_elements(self),
            *super().init_model_input_display_elements(),
        ]

    def update_model_input_display_on_sample_change(self):
        super().update_model_input_display_on_sample_change()
        PersonaChatVisualization.update_dialogue_structure_display(
            self, add_target=False
        )
