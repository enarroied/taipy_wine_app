from tracemalloc import stop
import pandas as pd
import geopandas as gpd
from sqlalchemy import column


def add_wine_colors():
    pass


def add_basic_stats(df_wine):
    """_summary_

    Args:
        df_wine (DataFrame): Wine production for several French Wine Regions

    Returns:
        df_wine_with_stats: The same DataFrame with 3 extra columns: Average, Min and Max
    """
    df_wine_with_stats = df_wine.reset_index(drop=True)
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

    # This is not for the stats, but this format is better for thje column name (used to display in dasboard)
    df_wine_with_stats = df_wine_with_stats.rename(columns={"wine_basin": "Region"})
    return df_wine_with_stats


def add_geometry(df_wine_with_stats, geometry):
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

    # This is a dirty patch to solve encoding problems:
    df_geometry["Bassin"] = df_geometry["Bassin"].str.replace(
        "VALLEE DU RHÃ”NE", "VALLEE DU RHÔNE"
    )

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
