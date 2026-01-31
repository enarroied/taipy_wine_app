from callbacks import on_change_all_regions


def overpass_ruff():
    on_change_all_regions()
    pass


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
    "title": "Production of White wines by Region (Million Liters)",
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

<|{selected_year}|selector|lov={year_list}|on_change=on_change_all_regions|dropdown|label=Choose Year|>

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

<|{selected_area}|toggle|lov={area_type_list}|on_change=on_change_all_regions|>

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
