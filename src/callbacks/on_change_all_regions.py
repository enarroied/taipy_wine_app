from taipy.gui import State

from algorithms import compute_region_data


def on_change_all_regions(state: State) -> None:
    """Update state based on a change in selected year and area type."""
    with state as s:
        data = compute_region_data(
            s.selected_year,
            s.selected_area,
            s.df_wine_production,
            s.df_wine_with_geometry,
        )

        s.df_wine_year = data["df_wine_year"]
        s.total_production = data["total_production"]
        s.red_rose_production = data["red_rose_production"]
        s.white_production = data["white_production"]
        s.df_map_red = data["df_map_red"]
        s.df_map_white = data["df_map_white"]
