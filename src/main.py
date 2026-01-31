from taipy.gui import Gui

from algorithms import create_df_region, get_df_map_color, get_df_wine_year_and_area
from config.config import df_wine_production, df_wine_with_geometry
from pages.all_regions import *
from pages.by_region import *

# Toggle theme: switch dark/light mode
root_md = """
<|toggle|theme|>
<center>\n<|navbar|>\n</center>
"""

stylekit = {
    "color-primary": "#CC3333",
    "color-secondary": "#E0C095",
    "color-background-light": "#F7E7CE",
    "color-background-dark": "#E0C095",
}

pages = {"/": root_md, "all_regions": all_regions_md, "by_region": by_region_md}


gui_multi_pages = Gui(pages=pages)

if __name__ == "__main__":
    # Variables for all_regions page
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

    df_wine_year = get_df_wine_year_and_area(
        selected_year, selected_area, df_wine_production
    )
    df_map_red = get_df_map_color(selected_year, "RED AND ROSE", df_wine_with_geometry)
    df_map_white = get_df_map_color(selected_year, "WHITE", df_wine_with_geometry)

    # Variables for the labels:
    total_production = df_wine_year["Production"].sum()
    red_rose_production = df_wine_year[df_wine_year["wine_type"] == "RED AND ROSE"][
        "Production"
    ].sum()
    white_production = df_wine_year[df_wine_year["wine_type"] == "WHITE"][
        "Production"
    ].sum()

    # variables for by_region page
    list_of_regions = df_wine_with_geometry["Region"].unique().tolist()
    selected_region = "SUD-OUEST"

    df_region_red, df_region_white = create_df_region(
        df_wine_with_geometry, selected_region
    )

    gui_multi_pages.run(
        use_reloader=True,
        title="Wine 🍷 production by Region and Year",
        dark_mode=False,
        stylekit=stylekit,
    )
