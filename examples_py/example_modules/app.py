import flask

from visuallm.server import Server

from .components.bar_chart_component_advanced import BarChartComponentAdvanced
from .components.bar_chart_component_simple import BarChartComponentSimple
from .components.collapsible_subcomponent import ComponentWithSubcomponents
from .components.horizontal_multi_radio_component import HorizontalMultiRadioComponent
from .components.reloadable_component import ReloadableComponent
from .components.selector_change_subselectors import SelectorChangingComponent
from .components.selector_component import SelectorComponent
from .components.selector_failing_component import SelectorFailingComponent
from .components.table_component import TableComponent
from .components.text_input_component import TextInputComponent
from .components.two_tables_component import TwoTablesComponent


def create_app() -> flask.Flask:
    flask_app = Server(
        __name__,
        [
            ComponentWithSubcomponents(),
            BarChartComponentAdvanced(),
            BarChartComponentSimple(),
            BarChartComponentSimple(long_contexts=True, title="Long Contexts BarChart"),
            TableComponent(),
            TwoTablesComponent(),
            SelectorComponent(),
            TextInputComponent(),
            SelectorFailingComponent(),
            SelectorChangingComponent(),
            HorizontalMultiRadioComponent(),
            ReloadableComponent(),
        ],
    )
    app = flask_app.app
    return app


if __name__ == "__main__":
    app = create_app()
