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


def get_df_map_color(year, color):
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


def get_df_wine_year_and_area(year, area_type):
    df_wine_year = df_wine_production[[area_type, "wine_type"]].copy()

    df_wine_year["Production"] = df_wine_production[year] / 10

    df_wine_year = df_wine_year.reset_index(drop=True)

    df_wine_year = df_wine_year.rename(columns={area_type: "Region"})

    df_wine_year = df_wine_year.groupby(["Region", "wine_type"]).sum()
    df_wine_year = df_wine_year.reset_index()
    df_wine_year = df_wine_year.sort_values(by=["Production"])

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


def on_change(state):
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


bar_chart_layout = {"yaxis": {"range": [0, 600]}}

property_barchart_red_rose = {
    "type": "bar",
    "x": "Region",
    "y[1]": "Production",
    "color[1]": "#900020",
    "title": "Production of Red wines (Million Liters)",
}

property_barchart_white = {
    "type": "bar",
    "x": "Region",
    "y[1]": "Production",
    "color[1]": "#E0C095",
    "title": f"Production of White wines (Million Liters)",
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
        "style": "stamen-toner",
        "center": {"lat": 46, "lon": 1.9},
        "zoom": 5,
    },
}

layout_map_white = {
    "title": "Production of white wines, per Region - Million Liters",
    "dragmode": "zoom",
    "mapbox": {
        "style": "stamen-toner",
        "center": {"lat": 46, "lon": 1.9},
        "zoom": 5,
    },
}

options_map = {
    "unselected": {"marker": {"opacity": 0.8}},
    "hovertemplate": "<b>%{text}</b>" + "<extra></extra>",
}

##############################################################################################################


all_regions_md = """

<|layout|columns= 1 2|

<|{selected_year}|selector|lov={year_list}|on_change=on_change|dropdown|label=Choose Year|>

# AOC Wine production | **<|{selected_year}|text|raw|> Campaign**{: .color-primary} | All Regions
|>


<|layout|columns=1 1 1|
<total_production|
## **Total:**{: .color-primary}
###<|{f'{int(total_production / 10) } Million Liters'}|>
|total_production>

<red_rose_production|
## **Red / Rosé:**{: .color-primary}
###<|{f'{int(red_rose_production / 10) } Million Liters'}|>
|red_rose_production>

<white_production|
## **White:**{: .color-primary}
###<|{f'{int(white_production / 10) } Million Liters'}|>
|white_production>
|>

## Production **by <|{selected_area}|text|raw|>**{: .color-primary}

<|{selected_area}|toggle|lov={area_type_list}|on_change=on_change|>

<|layout|columns=1 1|
<|{df_wine_year[df_wine_year["wine_type"] == "RED AND ROSE"]}|chart|properties={property_barchart_red_rose}|layout={bar_chart_layout}|>

<|{df_wine_year[df_wine_year["wine_type"] == "WHITE"]}|chart|properties={property_barchart_white}|layout={bar_chart_layout}|>
|>

## Production Maps, **<|{selected_year}|text|raw|>**{: .color-primary}:

<|layout|columns=1 1|
<|{df_map_red}|chart|type=scattermapbox|lat=latitude|lon=longitude|marker={marker_map_red}|layout={layout_map_red}|text=text|mode=markers|height=600px|options={options_map}|>

<|{df_map_white}|chart|type=scattermapbox|lat=latitude|lon=longitude|marker={marker_map_white}|layout={layout_map_white}|text=text|mode=markers|height=600px|options={options_map}|>
|>


## Data for all the regions:
<|{df_wine_production}|table|height=400px|width=100%|>


"""
