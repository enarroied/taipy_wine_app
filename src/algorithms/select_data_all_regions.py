import pandas as pd


def get_df_map_color(
    year: str, color: str, df_wine_with_geometry: pd.DataFrame
) -> pd.DataFrame:
    """Create a DataFrame for map coloring based on wine production data.

    Takes a specific year and wine color, and extracts relevant information from the
    original wine production DataFrame (`df_wine_with_geometry`). It creates a DataFrame
    suitable for map coloring, including information about regions, latitude, longitude,
    production, size, and text (a field to display the hover in the map).

    Args:
        year (str): The selected year for wine production data.
        color (str): The selected wine color (e.g., 'RED AND ROSE', 'WHITE').
        df_wine_with_geometry (pd.DataFrame, optional): DataFrame containing wine
            production and geographical information. Defaults to the global variable
            `df_wine_with_geometry`.

    Returns:
        df_map_color (pd.DataFrame): A DataFrame with information for map coloring.
    """

    df_geometry_color = df_wine_with_geometry[
        df_wine_with_geometry["wine_type"] == color
    ].copy()

    df_map_color = df_geometry_color[["Region", "latitude", "longitude"]]

    # Production is divided by 10 to show million Liters
    df_map_color["Production"] = df_geometry_color[year] / 10

    # to display and acceptable size of the dots on the map, dividing by 5 is arbitrary:
    df_map_color["size"] = df_map_color["Production"] / 5
    df_map_color["text"] = (
        df_map_color["Region"] + ": " + df_map_color["Production"].astype(str) + " Ml"
    )

    return df_map_color


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
        df_wine_production (pd.DataFrame, optional): DataFrame with wine production
            data. Defaults to the global variable `df_wine_production`.

    Returns:
        df_wine_year (pd.DataFrame): DataFrame with information about wine production.
    """

    df_wine_year = df_wine_production[[area_type, "wine_type"]].copy()

    # Production is divided by 10 to show million Liters
    df_wine_year["Production"] = df_wine_production[year] / 10
    df_wine_year = df_wine_year.reset_index(drop=True)
    df_wine_year = df_wine_year.rename(columns={area_type: "Region"})

    df_wine_year = df_wine_year.groupby(["Region", "wine_type"]).sum()
    df_wine_year = df_wine_year.reset_index()
    df_wine_year = df_wine_year.sort_values(by=["Production"])

    # Add a column to display a cleaner and shorter label in the bar chart
    df_wine_year["Wine Region"] = (
        (df_wine_year["Region"].str.replace(r"[a-zA-Z]/ ", "", regex=True))
        .str.replace(r" \(.+", "", regex=True)
        .str.replace(r" including.+", "", regex=True)
    )

    return df_wine_year
