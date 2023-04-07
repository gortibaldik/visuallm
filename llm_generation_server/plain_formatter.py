from llm_generation_server.format import FormattedContext

class PlainFormatter:
    def __init__(self, content: str = ""):
        self.content = content
    
    def format(self):
        return FormattedContext(
            "plain",
            self.content
        )