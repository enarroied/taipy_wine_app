from taipy.gui import State

from algorithms import get_df_map_color, get_df_wine_year_and_area


def on_change_all_regions(state: State) -> None:
    """Update state based on a change in selected year and area type.

    This function takes the current state (`state`) and updates relevant attributes
        based on a change in the selected year and area type. It calculates total
        production, production for red and white wines, and updates map DataFrames
        for red and white wines.

    Args:
        state (Any): The current state object.

    Returns:
        None
    """
    with state as s:
        df_wine_year = get_df_wine_year_and_area(
            s.selected_year, s.selected_area, s.df_wine_production
        )
        s.df_wine_year = df_wine_year.copy()
        # Update the labels:
        s.total_production = df_wine_year["Production"].sum()
        s.red_rose_production = df_wine_year[
            df_wine_year["wine_type"] == "RED AND ROSE"
        ]["Production"].sum()
        s.white_production = df_wine_year[df_wine_year["wine_type"] == "WHITE"][
            "Production"
        ].sum()

        # Update map dataframes:
        s.df_map_red = get_df_map_color(
            s.selected_year, "RED AND ROSE", s.df_wine_with_geometry
        )
        s.df_map_white = get_df_map_color(
            s.selected_year, "WHITE", s.df_wine_with_geometry
        )
