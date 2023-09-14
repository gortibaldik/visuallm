from visuallm.server import Server

from .components.bar_chart_component_advanced import BarChartComponentAdvanced
from .components.bar_chart_component_simple import BarChartComponentSimple
from .components.selector_component import SelectorComponent
from .components.table_component import TableComponent
from .components.text_input_component import TextInputComponent
from .components.two_tables_component import TwoTablesComponent

flask_app = Server(
    __name__,
    [
        BarChartComponentAdvanced(),
        BarChartComponentSimple(),
        BarChartComponentSimple(long_contexts=True, title="Long Contexts BarChart"),
        TableComponent(),
        TwoTablesComponent(),
        SelectorComponent(),
        TextInputComponent(),
    ],
)
app = flask_app.app
