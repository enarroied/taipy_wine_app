import pandas as pd


def _prepare_map_data(
    year: str, wine_type: str, df_wine_with_geometry: pd.DataFrame
) -> pd.DataFrame:
    """Create a DataFrame for map coloring based on wine production data.

    Args:
        year (str): The selected year for wine production data.
        wine_type (str): The wine type to filter for (e.g., 'RED AND ROSE', 'WHITE').
        df_wine_with_geometry (pd.DataFrame): DataFrame containing wine production
            and geographical information.

    Returns:
        pd.DataFrame: A DataFrame with columns Region, latitude, longitude,
            Production, size, and text for map visualization.
    """
    df_geometry_color = df_wine_with_geometry[
        df_wine_with_geometry["wine_type"] == wine_type
    ].copy()

    df_map_color = df_geometry_color[["Region", "latitude", "longitude"]].copy()
    df_map_color["Production"] = df_geometry_color[year] / 10
    df_map_color["size"] = df_map_color["Production"] / 5
    df_map_color["text"] = (
        df_map_color["Region"] + ": " + df_map_color["Production"].astype(str) + " Ml"
    )

    return df_map_color


def get_df_map_red_rose(year: str, df_wine_with_geometry: pd.DataFrame) -> pd.DataFrame:
    """Create map data for RED AND ROSE wine production.

    Args:
        year (str): The selected year for wine production data.
        df_wine_with_geometry (pd.DataFrame): DataFrame containing wine production
            and geographical information.

    Returns:
        pd.DataFrame: Map visualization data for red and rosé wines.
    """
    return _prepare_map_data(year, "RED AND ROSE", df_wine_with_geometry)


def get_df_map_white(year: str, df_wine_with_geometry: pd.DataFrame) -> pd.DataFrame:
    """Create map data for WHITE wine production.

    Args:
        year (str): The selected year for wine production data.
        df_wine_with_geometry (pd.DataFrame): DataFrame containing wine production
            and geographical information.

    Returns:
        pd.DataFrame: Map visualization data for white wines.
    """
    return _prepare_map_data(year, "WHITE", df_wine_with_geometry)


def get_df_wine_year_and_area(
    year: str, area_type: str, df_wine_production: pd.DataFrame
) -> pd.DataFrame:
    """Create a DataFrame for wine production based on a specific year and area type.

    This function takes a specific year and area type, and extracts relevant information
        from the original wine production DataFrame (`df_wine_production`). It creates
        a DataFrame suitable for displaying wine production data for a specified year
        and area type.

    Args:
        year (str): The selected year for wine production data.
        area_type (str): The selected area type (e.g., 'AOC', 'Region').
        df_wine_production (pd.DataFrame): DataFrame with wine production data.

    Returns:
        df_wine_year (pd.DataFrame): DataFrame with information about wine production.
    """
    df_wine_year = df_wine_production[[area_type, "wine_type"]].copy()
    df_wine_year["Production"] = df_wine_production[year] / 10
    df_wine_year = df_wine_year.reset_index(drop=True)
    df_wine_year = df_wine_year.rename(columns={area_type: "Region"})

    df_wine_year = df_wine_year.groupby(["Region", "wine_type"]).sum()
    df_wine_year = df_wine_year.reset_index()
    df_wine_year = df_wine_year.sort_values(by=["Production"])

    df_wine_year["Wine Region"] = (
        (df_wine_year["Region"].str.replace(r"[a-zA-Z]/ ", "", regex=True))
        .str.replace(r" \(.+", "", regex=True)
        .str.replace(r" including.+", "", regex=True)
    )

    return df_wine_year
