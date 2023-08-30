from taipy.core.config import Config
import pandas as pd
from config.config import df_wine_production, df_wine_with_geometry

list_of_regions = df_wine_with_geometry["Region"].unique().tolist()
selected_region = "SUD-OUEST"


def clean_df_region_color(df_region_color):
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


def create_df_region(selected_region):
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


def on_change_region(state):
    state.df_region_red, state.df_region_white = create_df_region(state.selected_region)
    pass


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

by_region_md = """

<|layout|columns= 1 2|

<|{selected_region}|selector|lov={list_of_regions}|on_change=on_change_region|dropdown|label=Choose Region|>
# Wine production | **by Region**{: .color-primary}

|>

# Charts:

<|layout|columns=1 1|

<|{df_region_red}|chart|properties={property_plot_red}|layout={plot_chart_layout}|>

<|{df_region_white}|chart|properties={property_plot_white}|layout={plot_chart_layout}|>

|>


"""
