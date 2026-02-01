from typing import List, Tuple

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


def create_df_region(
    df_wine_with_geometry: pd.DataFrame, selected_region: str, year_cols: List
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create DataFrames for red and white wine production statistics
        for a selected region.

    Takes a selected region (`selected_region`) and extracts relevant information from
        the original wine production DataFrame (`df_wine_with_geometry`). It creates
        separate DataFrames for red and white wine production.

    Args:
        selected_region (str): The selected wine region.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames: one for
            red wine ('df_region_red') and one for white wine ('df_region_white').
    """
    df_region = df_wine_with_geometry.copy()
    df_region = df_region[df_region["Region"] == selected_region]

    df_region_red = df_region[df_region["wine_type"] == "RED AND ROSE"].reset_index(
        drop=True
    )
    df_region_white = df_region[df_region["wine_type"] == "WHITE"].reset_index(
        drop=True
    )
    if selected_region not in ("CHAMPAGNE", "ALSACE ET EST"):
        df_region_red = clean_df_region_color(df_region_red)
    else:
        df_region_red = pd.DataFrame.from_dict(
            {
                "Harvest": [0] * len(year_cols),
                "years": year_cols,
            }
        )
    df_region_white = clean_df_region_color(df_region_white)
    return (df_region_red, df_region_white)
