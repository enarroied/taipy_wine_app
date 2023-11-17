from taipy.core.config import Config

from config.config import df_wine_production, df_wine_with_geometry

# This is so by_region can use it functions (better way??):
from pages.by_region import *

selected_year = "average"
year_list = [
    "average",
    "08/09",
    "09/10",
    "10/11",
    "11/12",
    "12/13",
    "13/14",
    "14/15",
    "15/16",
    "16/17",
    "17/18",
    "18/19",
]

area_type_list = ["AOC", "Region"]
selected_area = area_type_list[0]


def get_df_map_color(
    year: str, color: str, df_wine_with_geometry: pd.DataFrame = df_wine_with_geometry
) -> pd.DataFrame:
    """Create a DataFrame for map coloring based on wine production data.

    This function takes a specific year and wine color, and extracts relevant information
    from the original wine production DataFrame (`df_wine_with_geometry`). It creates a DataFrame
    suitable for map coloring, including information about regions, latitude, longitude, production,
    size, and text.

    Args:
        year (str): The selected year for wine production data.
        color (str): The selected wine color (e.g., 'RED AND ROSE', 'WHITE').
        df_wine_with_geometry (pd.DataFrame, optional): DataFrame containing wine production and
                                                         geographical information. Defaults to
                                                         the global variable `df_wine_with_geometry`.

    Returns:
        df_map_color (pd.DataFrame): A DataFrame with information for map coloring.
    """

    df_geometry_color = df_wine_with_geometry[
        df_wine_with_geometry["wine_type"] == color
    ].copy()

    df_map_color = df_geometry_color[["Region", "latitude", "longitude"]]

    # Production is divided by 10 to show million Liters
    df_map_color["Production"] = df_geometry_color[year] / 10

    # this is only to display and acceptable size of the dots on the map, dividing by 5 is arbitrary:
    df_map_color["size"] = df_map_color["Production"] / 5
    df_map_color["text"] = (
        df_map_color["Region"] + ": " + df_map_color["Production"].astype(str) + " Ml"
    )

    print(df_map_color.head())
    return df_map_color


def get_df_wine_year_and_area(
    year: str, area_type: str, df_wine_production: pd.DataFrame = df_wine_production
) -> pd.DataFrame:
    """Create a DataFrame for wine production based on a specific year and area type.

    This function takes a specific year and area type, and extracts relevant information
    from the original wine production DataFrame (`df_wine_production`). It creates a DataFrame
    suitable for displaying wine production data for a specified year and area type.

    Args:
        year (str): The selected year for wine production data.
        area_type (str): The selected area type (e.g., 'AOC', 'Region').
        df_wine_production (pd.DataFrame, optional): DataFrame containing wine production data.
                                                      Defaults to the global variable `df_wine_production`.

    Returns:
        df_wine_year (pd.DataFrame): A DataFrame with information for displaying wine production data.
    """

    df_wine_year = df_wine_production[[area_type, "wine_type"]].copy()

    df_wine_year["Production"] = df_wine_production[year] / 10

    df_wine_year = df_wine_year.reset_index(drop=True)

    df_wine_year = df_wine_year.rename(columns={area_type: "Region"})

    df_wine_year = df_wine_year.groupby(["Region", "wine_type"]).sum()
    df_wine_year = df_wine_year.reset_index()
    df_wine_year = df_wine_year.sort_values(by=["Production"])

    # Add a column to display a cleaner and shorter label in the bar chart

    df_wine_year["Wine Region"] = (
        (df_wine_year["Region"].str.replace(r"[a-zA-Z]/ ", "", regex=True))
        .str.replace(r" \(.+", "", regex=True)
        .str.replace(r" including.+", "", regex=True)
    )

    return df_wine_year


df_wine_year = get_df_wine_year_and_area(selected_year, selected_area)

df_map_red = get_df_map_color(selected_year, "RED AND ROSE")
df_map_white = get_df_map_color(selected_year, "WHITE")

# Variables for the labels:
total_production = df_wine_year["Production"].sum()
red_rose_production = df_wine_year[df_wine_year["wine_type"] == "RED AND ROSE"][
    "Production"
].sum()
white_production = df_wine_year[df_wine_year["wine_type"] == "WHITE"][
    "Production"
].sum()


def on_change(state: Any) -> None:
    """Update state based on a change in selected year and area type.

    This function takes the current state (`state`) and updates relevant attributes based on a
    change in the selected year and area type. It calculates total production, production for red
    and white wines, and updates map DataFrames for red and white wines.

    Args:
        state (Any): The current state object.

    Returns:
        None
    """

    print("Chosen year: ", state.selected_year)
    print("Choose region type: ", state.selected_area)
    state.df_wine_year = get_df_wine_year_and_area(
        state.selected_year, state.selected_area
    )
    # Update the labels:
    state.total_production = state.df_wine_year["Production"].sum()
    state.red_rose_production = state.df_wine_year[
        df_wine_year["wine_type"] == "RED AND ROSE"
    ]["Production"].sum()
    state.white_production = state.df_wine_year[df_wine_year["wine_type"] == "WHITE"][
        "Production"
    ].sum()

    # Update map dataframes:
    state.df_map_red = get_df_map_color(state.selected_year, "RED AND ROSE")
    state.df_map_white = get_df_map_color(state.selected_year, "WHITE")


##############################################################################################################
##                                      Chart properties:                                                   ##
##############################################################################################################

bar_chart_layout = {
    "yaxis": {"range": [0, 600]},
    "xaxis": {"automargin": True},
    "xlabel": "None",
}

property_barchart_red_rose = {
    "type": "bar",
    "x": "Wine Region",
    "y[1]": "Production",
    "color[1]": "#900020",
    "title": "Production of Red wines by Region (Million Liters)",
}

property_barchart_white = {
    "type": "bar",
    "x": "Wine Region",
    "y[1]": "Production",
    "color[1]": "#E0C095",
    "title": f"Production of White wines by Region (Million Liters)",
}

##############################################################################################################
##                                      For the map:                                                        ##
##############################################################################################################
marker_map_white = {
    "color": "Production",
    "size": "size",
    "showscale": True,
    "colorscale": "Viridis",  # No better colormap found
}

marker_map_red = {
    "color": "Production",
    "size": "size",
    "showscale": True,
    "colorscale": "RdBu",
}

layout_map_red = {
    "title": "Production of red wines, per Region - Million Liters",
    "dragmode": "zoom",
    "mapbox": {
        # "style": "stamen-toner",
        "style": "open-street-map",
        "center": {"lat": 46, "lon": 1.9},
        "zoom": 5,
    },
}

layout_map_white = {
    "title": "Production of white wines, per Region - Million Liters",
    "dragmode": "zoom",
    "mapbox": {
        # "style": "stamen-toner",
        "style": "open-street-map",
        "center": {"lat": 46, "lon": 1.9},
        "zoom": 5,
    },
}

options_map = {
    "unselected": {"marker": {"opacity": 0.8}},
    "hovertemplate": "<b>%{text}</b>" + "<extra></extra>",
}

##############################################################################################################
##                                      Taipy Code:                                                         ##
##############################################################################################################

all_regions_md = """

<|{selected_year}|selector|lov={year_list}|on_change=on_change|dropdown|label=Choose Year|>

# AOC Wine production | **<|{selected_year}|text|raw|> Campaign**{: .color-primary} | All Regions

<|layout|columns=1 1 1|

<|card card-bg|
## **Total:**{: .color-primary}
\n
### <|{f'{int(total_production / 10) } Million Liters'}|>
|>
<|card card-bg|
## **Red / Rosé:**{: .color-primary}
\n
###<|{f'{int(red_rose_production / 10) } Million Liters'}|>
|>
<|card card-bg|
## **White:**{: .color-primary}
\n
###<|{f'{int(white_production / 10) } Million Liters'}|>
|>
|>


## Production **by <|{selected_area}|text|raw|>**{: .color-primary}

<|{selected_area}|toggle|lov={area_type_list}|on_change=on_change|>

<|layout|columns=1 1|
<|{df_wine_year[df_wine_year["wine_type"] == "RED AND ROSE"]}|chart|properties={property_barchart_red_rose}|layout={bar_chart_layout}|height=800px|>

<|{df_wine_year[df_wine_year["wine_type"] == "WHITE"]}|chart|properties={property_barchart_white}|layout={bar_chart_layout}|height=800px|>
|>

## Production Maps, **<|{selected_year}|text|raw|>**{: .color-primary}:

<|layout|columns=1 1|
<|{df_map_red}|chart|type=scattermapbox|lat=latitude|lon=longitude|marker={marker_map_red}|layout={layout_map_red}|text=text|mode=markers|height=600px|options={options_map}|>

<|{df_map_white}|chart|type=scattermapbox|lat=latitude|lon=longitude|marker={marker_map_white}|layout={layout_map_white}|text=text|mode=markers|height=600px|options={options_map}|>
|>

## Data for all the regions:
<|{df_wine_production}|table|height=400px|width=100%|filter[AOC]=True|filter[Region]=True|filter[wine_type]=True|>
"""
