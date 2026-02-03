import taipy as tp
from taipy import Orchestrator
from taipy.gui import Gui

from algorithms import (
    compute_region_data,
    create_df_region_red,
    create_df_region_white,
)
from config.config import sc_wine_scenario
from pages import all_regions_page, by_region_page, root_page

pages = {"/": root_page, "all_regions": all_regions_page, "by_region": by_region_page}

gui_multi_pages = Gui(pages=pages, css_file="./css/main.css")

if __name__ == "__main__":
    Orchestrator().run()
    sc_wine = tp.create_scenario(sc_wine_scenario)
    sc_wine.submit()

    df_wine_production = sc_wine.wine_production_with_stats.read()
    df_wine_with_geometry = sc_wine.wine_production_with_geometry.read()

    # Variables for all_regions page
    selected_year = "average"
    year_list = sc_wine.year_list.read()
    year_list_for_selector = [selected_year] + year_list

    area_type_list = ["AOC", "Region"]
    selected_area = area_type_list[0]

    region_data = compute_region_data(
        selected_year, selected_area, df_wine_production, df_wine_with_geometry
    )

    df_wine_year = region_data["df_wine_year"]
    df_map_red = region_data["df_map_red"]
    df_map_white = region_data["df_map_white"]
    total_production = region_data["total_production"]
    red_rose_production = region_data["red_rose_production"]
    white_production = region_data["white_production"]

    # variables for by_region page
    list_of_regions = df_wine_with_geometry["Region"].unique().tolist()
    selected_region = "SUD-OUEST"

    df_region_red = create_df_region_red(
        df_wine_with_geometry, selected_region, year_list
    )
    df_region_white = create_df_region_white(
        df_wine_with_geometry, selected_region, year_list
    )

    # Chart properties:

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
    # For the map:
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

    gui_multi_pages.run(
        use_reloader=True,
        title="Wine 🍷 production by Region and Year",
        dark_mode=False,
    )
