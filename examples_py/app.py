from llm_generation_server.server import Server

from .bar_chart_component_advanced import BarChartComponentAdvanced
from .bar_chart_component_simple import BarChartComponentSimple
from .selector_component import SelectorComponent
from .table_component import TableComponent

flask_app = Server(
    __name__,
    [
        BarChartComponentAdvanced(),
        BarChartComponentSimple(),
        BarChartComponentSimple(long_contexts=True, title="Long Contexts BarChart"),
        TableComponent(),
        SelectorComponent(),
    ],
)
app = flask_app.app
