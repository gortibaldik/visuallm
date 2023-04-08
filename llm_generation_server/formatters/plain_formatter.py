from llm_generation_server.formatters.format import FormattedContext

class PlainFormatter:
    def __init__(self, content: str = ""):
        self.content = content
    
    def format(self):
        return FormattedContext(
            "plain",
            self.content
        )