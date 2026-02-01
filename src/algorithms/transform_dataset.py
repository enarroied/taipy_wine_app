from typing import List

import geopandas as gpd
import pandas as pd


def add_basic_stats(df_wine: pd.DataFrame, year_cols: List) -> pd.DataFrame:
    """Add basic statistics to a DataFrame containing wine production data.

    This function calculates the minimum, maximum, and average wine production values
    for each row in the input DataFrame based on yearly data. The resulting DataFrame
    includes three additional columns: 'min', 'max', and 'average'.

    Args:
        df_wine (pd.DataFrame): A DataFrame containing wine production data for various
         French wine regions.
        year_cols (List): List of year column names to compute statistics over.

    Returns:
        df_wine_with_stats (pd.DataFrame): A new DataFrame with additional columns
         ('min', 'max', 'average') representing the calculated statistics for each row.
    """
    df_wine_with_stats = df_wine.copy()
    df_wine_years = df_wine_with_stats[year_cols]

    df_wine_with_stats["min"] = df_wine_years.min(axis=1)
    df_wine_with_stats["max"] = df_wine_years.max(axis=1)
    df_wine_with_stats["average"] = round(df_wine_years.mean(axis=1), 2)
    df_wine_with_stats = df_wine_with_stats.rename(columns={"wine_basin": "Region"})

    return df_wine_with_stats


def add_geometry(
    df_wine_with_stats: pd.DataFrame, geometry: pd.DataFrame, year_cols: List
) -> pd.DataFrame:
    """Add geographical information to DataFrame containing wine production statistics.

    Takes a DataFrame with wine production statistics (`df_wine_with_stats`) and a
    DataFrame with geographical information (`geometry`). It adds geographical data to
    the wine production DataFrame (including latitude and longitude).

    Args:
        df_wine_with_stats (pd.DataFrame): DataFrame with wine production statistics
            for various regions and wine types.
        geometry (pd.DataFrame): DataFrame with geometrical information, including the
            'geometry' column containing the geographical shapes.
        year_cols (List): List of year column names used to recompute the average.

    Returns:
        df_wine_with_geometry (pd.DataFrame): New DataFrame with additional geographical
         information, including latitude and longitude, added to wine production data.
    """
    df_wine_with_geometry = _drop_subset_aocs(df_wine_with_stats.copy())
    df_wine_with_geometry = _aggregate_by_region(df_wine_with_geometry, year_cols)

    df_geometry = _extract_lat_lon(geometry)

    df_wine_with_geometry = df_wine_with_geometry.merge(
        df_geometry, left_on="Region", right_on="Bassin"
    )
    return df_wine_with_geometry.drop("Bassin", axis=1)


def _drop_subset_aocs(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows whose AOC name contains '(subset)'.

    Subset AOCs are partial breakdowns of a parent AOC already present in the
    DataFrame.  Keeping them would cause double-counting during aggregation.

    Args:
        df (pd.DataFrame): DataFrame with an 'AOC' column.

    Returns:
        pd.DataFrame: Filtered copy with subset rows removed and index reset.
    """
    is_subset = df["AOC"].str.contains("(subset)", regex=False)
    return df.drop(df[is_subset].index).reset_index(drop=True)


def _aggregate_by_region(df: pd.DataFrame, year_cols: List) -> pd.DataFrame:
    """Aggregate production data per (Region, wine_type) and recalculate average.

    Drops per-AOC columns that are no longer meaningful after grouping, sums the
    year columns within each group, recomputes the average from those sums, and
    sorts descending by average.

    Args:
        df (pd.DataFrame): DataFrame that still carries 'AOC', 'min', 'max',
            and 'average' columns.
        year_cols (List): List of year column names used to recompute the average.

    Returns:
        pd.DataFrame: Grouped and sorted DataFrame with a fresh average column.
    """
    df = df.drop(["AOC", "min", "max", "average"], axis=1)
    df = df.groupby(["Region", "wine_type"]).sum().reset_index()
    df["average"] = round(df[year_cols].mean(axis=1), 2)
    return df.sort_values(by=["average"], ascending=False).reset_index(drop=True)


def _extract_lat_lon(geometry) -> pd.DataFrame:
    """Convert raw GeoJSON geometry into a flat DataFrame with latitude and longitude.

    Reprojects from EPSG:3857 (Web Mercator) to EPSG:4326 so that coordinates
    can be read directly as lat/lon.

    Args:
        geometry: GeoJSON feature collection (list of Feature dicts) in EPSG:3857.

    Returns:
        pd.DataFrame: DataFrame with 'Bassin', 'latitude', and 'longitude' columns.
    """
    df_geometry = gpd.GeoDataFrame.from_features(geometry, crs=3857)
    df_geometry = df_geometry.to_crs(epsg=4326)
    df_geometry["latitude"] = df_geometry["geometry"].y
    df_geometry["longitude"] = df_geometry["geometry"].x
    return df_geometry.drop("geometry", axis=1)
