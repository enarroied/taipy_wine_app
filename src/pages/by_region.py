from typing import Any

from algorithms import create_df_region
from config.config import df_wine_with_geometry


def on_change_region(state: Any) -> None:
    """Update red and white wine DataFrames based on a change in the selected region.

    This function takes the current state (`state`) and updates the red and white wine
    DataFrames (`df_region_red` and `df_region_white`) based on a change in the selected region.

    Args:
        state (Any): The current state object.

    Returns:
        None
    """
    state.df_region_red, state.df_region_white = create_df_region(
        df_wine_with_geometry, state.selected_region
    )


##############################################################################################################
##                                      Chart properties:                                                   ##
##############################################################################################################

plot_chart_layout = {"yaxis": {"range": [0, 600]}}

property_plot_white = {
    "type": "scatter",
    "mode": "lines",
    "x": "years",
    "y": "Harvest",
    "color": "#E0C095",
    "title": "Production of White wines (Million Liters)",
}

property_plot_red = {
    "type": "scatter",
    "mode": "lines",
    "x": "years",
    "y": "Harvest",
    "color": "#900020",
    "title": "Production of Red wines (Million Liters)",
}

##############################################################################################################
##                                      Taipy Code:                                                         ##
##############################################################################################################

by_region_md = """

<|layout|columns= 1 2|

<|{selected_region}|selector|lov={list_of_regions}|on_change=on_change_region|dropdown|label=Choose Region|>
# Wine production | **by Region**{: .color-primary}
|>

# Charts:

<|layout|columns= 1 1|
<|{df_region_red}|chart|properties={property_plot_red}|layout={plot_chart_layout}|>

<|{df_region_white}|chart|properties={property_plot_white}|layout={plot_chart_layout}|>
|>
"""
