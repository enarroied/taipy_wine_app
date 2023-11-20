from typing import Any, Tuple

import pandas as pd

from config.config import df_wine_with_geometry

list_of_regions = df_wine_with_geometry["Region"].unique().tolist()
selected_region = "SUD-OUEST"


def clean_df_region_color(df_region_color: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform a DataFrame containing region color information.

    This function takes a DataFrame (`df_region_color`) containing color information for a specific
    wine region. It performs cleaning operations, including dropping unnecessary columns and
    transposing the DataFrame for better representation.

    Args:
        df_region_color (pd.DataFrame): DataFrame containing color information for a specific wine region.

    Returns:
        pd.DataFrame: A cleaned and transformed DataFrame with columns 'Harvest' and 'years'.
    """
    df_region_color_clean = df_region_color.drop(
        ["Region", "wine_type", "average", "latitude", "longitude"], axis=1
    )

    years = df_region_color_clean.columns
    df_region_color_clean = df_region_color_clean.transpose().rename(
        columns={0: "Harvest"}
    )
    df_region_color_clean["Harvest"] = df_region_color_clean["Harvest"] / 10
    df_region_color_clean["years"] = years
    return df_region_color_clean


def create_df_region(selected_region: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create DataFrames for red and white wine production statistics for a selected region.

    This function takes a selected region (`selected_region`) and extracts relevant information
    from the original wine production DataFrame (`df_wine_with_geometry`). It creates separate
    DataFrames for red and white wine production, applying additional cleaning operations.

    Args:
        selected_region (str): The selected wine region.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames - one for red wine ('df_region_red')
        and one for white wine ('df_region_white').
    """
    df_region = df_wine_with_geometry.copy()
    df_region = df_region[df_region["Region"] == selected_region]

    df_region_red = df_region[df_region["wine_type"] == "RED AND ROSE"].reset_index(
        drop=True
    )
    df_region_white = df_region[df_region["wine_type"] == "WHITE"].reset_index(
        drop=True
    )
    if selected_region not in ("CHAMPAGNE", "ALSACE ET EST"):
        df_region_red = clean_df_region_color(df_region_red)
    else:
        df_region_red = pd.DataFrame.from_dict(
            {
                "Harvest": [0] * 10,
                "years": [
                    "08/09",
                    "09/10",
                    "10/11",
                    "11/12",
                    "12/13",
                    "13/14",
                    "14/15",
                    "15/16",
                    "17/18",
                    "18/19",
                ],
            }
        )
    df_region_white = clean_df_region_color(df_region_white)
    return (df_region_red, df_region_white)


df_region_red, df_region_white = create_df_region(selected_region)


def on_change_region(state: Any) -> None:
    """Update red and white wine DataFrames based on a change in the selected region.

    This function takes the current state (`state`) and updates the red and white wine
    DataFrames (`df_region_red` and `df_region_white`) based on a change in the selected region.

    Args:
        state (Any): The current state object.

    Returns:
        None
    """
    state.df_region_red, state.df_region_white = create_df_region(state.selected_region)


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
    "title": f"Production of White wines (Million Liters)",
}

property_plot_red = {
    "type": "scatter",
    "mode": "lines",
    "x": "years",
    "y": "Harvest",
    "color": "#900020",
    "title": f"Production of Red wines (Million Liters)",
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
