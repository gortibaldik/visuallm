from llm_generation_server.formatters.format import FormattedContext

class SampleSelectorFormatter:
    def __init__(self, sample_min: int, sample_max: int):
        self.sample_min = sample_min
        self.sample_max = sample_max
    
    def format(self):
        return FormattedContext(
            "sample_selector",
            dict(
                min=self.sample_min,
                max=self.sample_max,
            )
        )