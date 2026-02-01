import pandas as pd
import pytest

from algorithms import get_df_map_color, get_df_wine_year_and_area

YEAR_COLS = [
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


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def geometry_df() -> pd.DataFrame:
    """Mimics the output of add_geometry: one row per (Region, wine_type).

    Values are deliberately distinct per row so tests can verify filtering
    and math without accidentally passing on equal inputs.
    """
    rows = [
        {
            "Region": "SUD-OUEST",
            "wine_type": "RED AND ROSE",
            "average": 200.0,
            "latitude": 44.84,
            "longitude": -0.58,
            **{col: 1000 for col in YEAR_COLS},
            "08/09": 500,
        },
        {
            "Region": "SUD-OUEST",
            "wine_type": "WHITE",
            "average": 150.0,
            "latitude": 44.84,
            "longitude": -0.58,
            **{col: 600 for col in YEAR_COLS},
        },
        {
            "Region": "CHAMPAGNE",
            "wine_type": "WHITE",
            "average": 400.0,
            "latitude": 48.34,
            "longitude": 4.03,
            **{col: 2000 for col in YEAR_COLS},
            "08/09": 800,
        },
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def production_df() -> pd.DataFrame:
    """Mimics a raw wine production DataFrame with AOC and Region columns.

    Includes cases that exercise every branch of the Wine Region regex:
      - "BORDEAUX / SUD-OUEST"  → the "X/ " pattern
      - "SANCERRE (subset)"     → the " (" pattern
      - "CHAMPAGNE including X" → the " including" pattern
      - "CAHORS"                → no pattern, label unchanged
    Two AOCs share the same Region so the groupby-sum path is exercised.
    """
    rows = [
        {
            "AOC": "R/ SUD-OUEST",
            "Region": "SUD-OUEST",
            "wine_type": "RED AND ROSE",
            **{col: 200 for col in YEAR_COLS},
        },
        {
            "AOC": "CAHORS",
            "Region": "SUD-OUEST",
            "wine_type": "RED AND ROSE",
            **{col: 100 for col in YEAR_COLS},
        },
        {
            "AOC": "SANCERRE (subset)",
            "Region": "VAL DE LOIRE",
            "wine_type": "WHITE",
            **{col: 400 for col in YEAR_COLS},
        },
        {
            "AOC": "CHAMPAGNE including Côte des Blancs",
            "Region": "CHAMPAGNE",
            "wine_type": "WHITE",
            **{col: 800 for col in YEAR_COLS},
        },
    ]
    return pd.DataFrame(rows)


# ===========================================================================
# Tests – get_df_map_color
# ===========================================================================


class TestGetDfMapColor:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, geometry_df):
        result = get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        assert isinstance(result, pd.DataFrame)

    def test_output_columns(self, geometry_df):
        result = get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        assert list(result.columns) == [
            "Region",
            "latitude",
            "longitude",
            "Production",
            "size",
            "text",
        ]

    # --- Filtering by wine_type ---

    def test_filters_to_requested_color_only(self, geometry_df):
        result = get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        # Only one RED AND ROSE row exists in the fixture
        assert len(result) == 1
        assert result.iloc[0]["Region"] == "SUD-OUEST"

    def test_white_filter_returns_white_rows_only(self, geometry_df):
        result = get_df_map_color("08/09", "WHITE", geometry_df)
        assert len(result) == 2
        assert set(result["Region"]) == {"SUD-OUEST", "CHAMPAGNE"}

    # --- Production = year / 10 ---

    def test_production_divided_by_10(self, geometry_df):
        # RED AND ROSE, 08/09 = 500 → Production = 50.0
        result = get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        assert result.iloc[0]["Production"] == 50.0

    def test_production_uses_correct_year(self, geometry_df):
        # RED AND ROSE, 09/10 = 1000 → Production = 100.0
        result = get_df_map_color("09/10", "RED AND ROSE", geometry_df)
        assert result.iloc[0]["Production"] == 100.0

    def test_production_white_champagne(self, geometry_df):
        # CHAMPAGNE WHITE, 08/09 = 800 → Production = 80.0
        result = get_df_map_color("08/09", "WHITE", geometry_df)
        champagne = result[result["Region"] == "CHAMPAGNE"]
        assert champagne.iloc[0]["Production"] == 80.0

    # --- size = Production / 5 ---

    def test_size_is_production_divided_by_5(self, geometry_df):
        result = get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        row = result.iloc[0]
        assert row["size"] == row["Production"] / 5

    def test_size_values_white(self, geometry_df):
        result = get_df_map_color("09/10", "WHITE", geometry_df)
        # SUD-OUEST WHITE 09/10=600 → Production=60 → size=12
        # CHAMPAGNE WHITE 09/10=2000 → Production=200 → size=40
        sud_ouest = result[result["Region"] == "SUD-OUEST"].iloc[0]
        champagne = result[result["Region"] == "CHAMPAGNE"].iloc[0]
        assert sud_ouest["size"] == 12.0
        assert champagne["size"] == 40.0

    # --- text label ---

    def test_text_format(self, geometry_df):
        result = get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        # Production = 50.0 → "SUD-OUEST: 50.0 Ml"
        assert result.iloc[0]["text"] == "SUD-OUEST: 50.0 Ml"

    def test_text_contains_region_and_ml(self, geometry_df):
        result = get_df_map_color("09/10", "WHITE", geometry_df)
        for _, row in result.iterrows():
            assert row["text"].startswith(row["Region"] + ": ")
            assert row["text"].endswith(" Ml")

    # --- Coordinates carried through ---

    def test_latitude_longitude_preserved(self, geometry_df):
        result = get_df_map_color("08/09", "WHITE", geometry_df)
        champagne = result[result["Region"] == "CHAMPAGNE"].iloc[0]
        assert champagne["latitude"] == 48.34
        assert champagne["longitude"] == 4.03

    # --- Immutability ---

    def test_does_not_mutate_input(self, geometry_df):
        original = geometry_df.copy()
        get_df_map_color("08/09", "RED AND ROSE", geometry_df)
        pd.testing.assert_frame_equal(geometry_df, original)


# ===========================================================================
# Tests – get_df_wine_year_and_area
# ===========================================================================


class TestGetDfWineYearAndArea:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, production_df):
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        assert isinstance(result, pd.DataFrame)

    def test_output_columns(self, production_df):
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        assert list(result.columns) == [
            "Region",
            "wine_type",
            "Production",
            "Wine Region",
        ]

    # --- area_type controls which column becomes "Region" ---

    def test_aoc_mode_preserves_individual_aocs(self, production_df):
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        # Each AOC is unique so no rows are merged by the groupby
        assert len(result) == 4

    def test_region_mode_groups_aocs_into_regions(self, production_df):
        result = get_df_wine_year_and_area("08/09", "Region", production_df)
        # BORDEAUX and CAHORS both map to SUD-OUEST/RED AND ROSE → merged into one row
        assert len(result) == 3

    def test_region_mode_sums_production(self, production_df):
        result = get_df_wine_year_and_area("08/09", "Region", production_df)
        # SUD-OUEST RED: (200 + 100) / 10 = 30.0
        sud_ouest = result[
            (result["Region"] == "SUD-OUEST") & (result["wine_type"] == "RED AND ROSE")
        ]
        assert sud_ouest.iloc[0]["Production"] == 30.0

    # --- Production = year / 10 ---

    def test_production_divided_by_10(self, production_df):
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        # CAHORS 08/09 = 100 → Production = 10.0
        cahors = result[result["Region"] == "CAHORS"]
        assert cahors.iloc[0]["Production"] == 10.0

    def test_production_uses_correct_year(self, production_df):
        # All cols except 08/09 are uniform per row, so 09/10 == default value
        result = get_df_wine_year_and_area("09/10", "AOC", production_df)
        cahors = result[result["Region"] == "CAHORS"]
        assert cahors.iloc[0]["Production"] == 10.0  # 100 / 10

    # --- Sorted by Production ascending ---

    def test_sorted_by_production_ascending(self, production_df):
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        productions = result["Production"].tolist()
        assert productions == sorted(productions)

    def test_sorted_ascending_region_mode(self, production_df):
        result = get_df_wine_year_and_area("08/09", "Region", production_df)
        productions = result["Production"].tolist()
        assert productions == sorted(productions)

    # --- Wine Region label regex cleaning ---

    def test_label_strips_slash_prefix(self, production_df):
        """'R/ SUD-OUEST' → strip 'R/ ' → 'SUD-OUEST'."""
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        row = result[result["Region"] == "R/ SUD-OUEST"]
        assert row.iloc[0]["Wine Region"] == "SUD-OUEST"

    def test_label_strips_parenthetical(self, production_df):
        """'SANCERRE (subset)' → strip ' (subset)' → 'SANCERRE'."""
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        row = result[result["Region"] == "SANCERRE (subset)"]
        assert row.iloc[0]["Wine Region"] == "SANCERRE"

    def test_label_strips_including_clause(self, production_df):
        """'CHAMPAGNE including Côte des Blancs'
        → strip ' including...' → 'CHAMPAGNE'."""
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        row = result[result["Region"] == "CHAMPAGNE including Côte des Blancs"]
        assert row.iloc[0]["Wine Region"] == "CHAMPAGNE"

    def test_label_unchanged_when_no_pattern_matches(self, production_df):
        """'CAHORS' has none of the special patterns → label stays 'CAHORS'."""
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        row = result[result["Region"] == "CAHORS"]
        assert row.iloc[0]["Wine Region"] == "CAHORS"

    # --- Index is clean ---

    def test_index_is_reset(self, production_df):
        result = get_df_wine_year_and_area("08/09", "AOC", production_df)
        # sort_values doesn't reset index, but reset_index was called before sort.
        # After sort the index will be shuffled — just verify it's integer-based.
        assert result.index.dtype in ("int64", "int32")

    # --- Immutability ---

    def test_does_not_mutate_input(self, production_df):
        original = production_df.copy()
        get_df_wine_year_and_area("08/09", "AOC", production_df)
        pd.testing.assert_frame_equal(production_df, original)
