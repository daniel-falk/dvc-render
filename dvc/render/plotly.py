import json
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, Optional

from dvc.render.base import Renderer

if TYPE_CHECKING:
    from dvc.compare import TabularData


class ParallelCoordinatesRenderer(Renderer):
    TYPE = "plotly"

    DIV = """
    <div id = "{id}">
        <script type = "text/javascript">
            var plotly_data = {partial};
            Plotly.newPlot("{id}", plotly_data.data, plotly_data.layout);
        </script>
    </div>
    """

    SCRIPTS = """
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    """

    # pylint: disable=W0231
    def __init__(
        self, tabular_data: "TabularData", color_by: Optional[str] = None
    ):
        self.tabular_data = tabular_data
        self.color_by = color_by
        self.filename = "experiments"

    def partial_html(self, **kwargs):
        return self.as_json()

    def as_json(self, **kwargs) -> str:
        tabular_dict = defaultdict(list)
        for row in self.tabular_data.as_dict():
            for col_name, value in row.items():
                tabular_dict[col_name].append(str(value))

        trace: Dict[str, Any] = {"type": "parcoords", "dimensions": []}
        for label, values in tabular_dict.items():
            is_categorical = False

            try:
                float_values = [float(x) for x in values]
            except ValueError:
                is_categorical = True
                dummy_values = list(range(len(values)))

            if is_categorical:
                trace["dimensions"].append(
                    {
                        "label": label,
                        "values": dummy_values,
                        "tickvals": dummy_values,
                        "ticktext": values,
                    }
                )
            else:
                trace["dimensions"].append(
                    {"label": label, "values": float_values}
                )

            if label == self.color_by:
                trace["line"] = {
                    "color": dummy_values if is_categorical else float_values,
                    "showscale": True,
                }
                if is_categorical:
                    trace["line"]["colorbar"] = {
                        "tickmode": "array",
                        "tickvals": dummy_values,
                        "ticktext": values,
                    }

        return json.dumps({"data": [trace], "layout": {}})
