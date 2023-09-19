import flask

from visuallm.server import Server

from .bar_chart_component_advanced import BarChartComponentAdvanced
from .bar_chart_component_simple import BarChartComponentSimple
from .selector_component import SelectorComponent
from .table_component import TableComponent
from .text_input_component import TextInputComponent
from .two_tables_component import TwoTablesComponent


def create_app() -> flask.Flask:
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
    return app


if __name__ == "__main__":
    app = create_app()
