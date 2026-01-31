from callbacks import on_change_region


def overpass_ruff():
    on_change_region()
    pass


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
