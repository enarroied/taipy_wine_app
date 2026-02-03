from typing import List

import pandas as pd


def clean_df_region_color(df_region_color: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform a DataFrame containing region color information.

    This function takes a DataFrame (`df_region_color`) with color information for a
        specific wine region. It performs cleaning operations, including dropping
        unnecessary columns and transposing the DataFrame for better representation.

    Args:
        df_region_color (pd.DataFrame): DataFrame with color information
            for specific region.

    Returns:
        pd.DataFrame: Cleaned and transformed DataFrame with columns 'Harvest'
            and 'years'.
    """
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


def create_df_region_red(
    df_wine_with_geometry: pd.DataFrame, selected_region: str, year_cols: List
) -> pd.DataFrame:
    """Create DataFrame for red and rosé wine production in a selected region.

    For CHAMPAGNE and ALSACE ET EST, which produce negligible red wine, returns
    a zero-filled fallback DataFrame. For all other regions, applies the standard
    cleaning transformation.

    Args:
        df_wine_with_geometry (pd.DataFrame): DataFrame with wine production and
            geographical information.
        selected_region (str): The wine region.
        year_cols (List): List of year column names.

    Returns:
        pd.DataFrame: Cleaned DataFrame with 'Harvest' and 'years' columns.
    """
    df_filtered = _filter_region_and_wine_type(
        df_wine_with_geometry, selected_region, "RED AND ROSE"
    )

    if df_filtered.empty:
        return _empty_harvest_dataframe(year_cols)

    return clean_df_region_color(df_filtered)


def create_df_region_white(
    df_wine_with_geometry: pd.DataFrame, selected_region: str, year_cols: List
) -> pd.DataFrame:
    """Create DataFrame for white wine production in a selected region.

    Args:
        df_wine_with_geometry (pd.DataFrame): DataFrame with wine production and
            geographical information.
        selected_region (str): The wine region.

    Returns:
        pd.DataFrame: Cleaned DataFrame with 'Harvest' and 'years' columns.
    """
    df_filtered = _filter_region_and_wine_type(
        df_wine_with_geometry, selected_region, "WHITE"
    )
    if df_filtered.empty:
        return _empty_harvest_dataframe(year_cols)
    return clean_df_region_color(df_filtered)


def _filter_region_and_wine_type(
    df_wine_with_geometry: pd.DataFrame, selected_region: str, wine_type: str
) -> pd.DataFrame:
    """Filter DataFrame to a specific region and wine type.

    Args:
        df_wine_with_geometry (pd.DataFrame): DataFrame with wine production and
            geographical information.
        selected_region (str): The wine region to filter to.
        wine_type (str): The wine type to filter to (e.g., 'RED AND ROSE', 'WHITE').

    Returns:
        pd.DataFrame: Filtered DataFrame containing only rows matching the region
            and wine type.
    """
    df_region = df_wine_with_geometry[
        df_wine_with_geometry["Region"] == selected_region
    ]
    return df_region[df_region["wine_type"] == wine_type].reset_index(drop=True)


def _empty_harvest_dataframe(year_cols: List) -> pd.DataFrame:
    """Create an empty harvest DataFrame when no data exists for a region/wine type.

    Returns a DataFrame with zero harvest values for all years, matching the
    structure expected after clean_df_region_color transformation.

    Args:
        year_cols (List): List of year column names.

    Returns:
        pd.DataFrame: DataFrame with 'Harvest' and 'years' columns, all harvests zero.
    """
    return pd.DataFrame({"Harvest": [0] * len(year_cols), "years": year_cols})
