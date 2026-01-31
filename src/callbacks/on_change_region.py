from taipy.gui import State

from algorithms import create_df_region
from config.config import df_wine_with_geometry


def on_change_region(state: State) -> None:
    """Update red and white wine DataFrames based on a change in the selected region.

    This function takes the current state (`state`) and updates the red and white wine
    DataFrames (`df_region_red` and `df_region_white`) based on a change in the selected region.

    Args:
        state (Any): The current state object.

    Returns:
        None
    """
    with state as s:
        state.df_region_red, state.df_region_white = create_df_region(
            df_wine_with_geometry, state.selected_region
        )
