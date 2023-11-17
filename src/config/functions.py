import pandas as pd
import geopandas as gpd


def add_basic_stats(df_wine: pd.DataFrame) -> pd.DataFrame:
    """Add basic statistics to a DataFrame containing wine production data.

    This function calculates the minimum, maximum, and average wine production values for each row
    in the input DataFrame based on yearly data. The resulting DataFrame includes three additional
    columns: 'min', 'max', and 'average'.

    Args:
        df_wine (pd.DataFrame): A DataFrame containing wine production data for various French wine regions.

    Returns:
        df_wine_with_stats (pd.DataFrame): A new DataFrame with additional columns ('min', 'max', 'average') representing
                   the calculated statistics for each row.
    """
    df_wine_with_stats = df_wine.copy()
    df_wine_years = df_wine_with_stats[
        [
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
    ]

    df_wine_with_stats["min"] = df_wine_years.min(axis=1)
    df_wine_with_stats["max"] = df_wine_years.max(axis=1)
    df_wine_with_stats["average"] = round(df_wine_years.mean(axis=1), 2)

    # Rename the "wine_basin" column for better readability in the dashboard
    df_wine_with_stats = df_wine_with_stats.rename(columns={"wine_basin": "Region"})
    return df_wine_with_stats


def add_geometry(
    df_wine_with_stats: pd.DataFrame, geometry: pd.DataFrame
) -> pd.DataFrame:
    """_summary_

    Args:
        df_wine_with_stats (_type_): _description_
        df_geometry (_type_): _description_

    Returns:
        _type_: _description_
    """
    df_geometry = gpd.GeoDataFrame.from_features(geometry, crs=3857)

    # Reproject to EPSG:4326 to be able to extract Lon and Lat
    df_geometry = df_geometry.to_crs(epsg=4326)

    df_wine_with_geometry = df_wine_with_stats

    # Drop the rows that are subsets (so we don't count in aggregation)
    rows_to_drop = df_wine_with_geometry["AOC"].str.contains("(subset)")
    df_wine_with_geometry = df_wine_with_geometry.drop(
        df_wine_with_geometry[rows_to_drop].index
    )
    df_wine_with_geometry = df_wine_with_geometry.reset_index(drop=True)

    # Drop the "AOC" column, as well as "min" and "max"
    df_wine_with_geometry = df_wine_with_geometry.drop(["AOC", "min", "max"], axis=1)

    df_wine_with_geometry = df_wine_with_geometry.groupby(["Region", "wine_type"]).sum()
    df_wine_with_geometry = df_wine_with_geometry.reset_index()
    df_wine_with_geometry = df_wine_with_geometry.sort_values(
        by=["average"], ascending=False
    ).reset_index(drop=True)

    # Extract latitude and longitude
    df_geometry["latitude"] = df_geometry["geometry"].y
    df_geometry["longitude"] = df_geometry["geometry"].x
    df_geometry = df_geometry.drop("geometry", axis=1)

    df_wine_with_geometry = pd.merge(
        df_wine_with_geometry, df_geometry, left_on="Region", right_on="Bassin"
    )

    df_wine_with_geometry = df_wine_with_geometry.drop("Bassin", axis=1)
    return df_wine_with_geometry
