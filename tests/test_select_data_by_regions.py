import pandas as pd
import pytest

from algorithms import (
    clean_df_region_color,
    create_df_region_red,
    create_df_region_white,
)

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


def _make_geometry_row(region: str, wine_type: str, values: dict | None = None) -> dict:
    """Build one row as it would look coming out of add_geometry."""
    base = {col: 100 for col in YEAR_COLS}
    if values:
        base.update(values)
    return {
        "Region": region,
        "wine_type": wine_type,
        "average": 100.0,
        "latitude": 44.84,
        "longitude": -0.58,
        **base,
    }


@pytest.fixture
def single_row_df() -> pd.DataFrame:
    """Single-row DataFrame ready for clean_df_region_color."""
    return pd.DataFrame([_make_geometry_row("SUD-OUEST", "RED AND ROSE")])


@pytest.fixture
def full_geometry_df() -> pd.DataFrame:
    """Multi-region DataFrame mimicking the output of add_geometry.

    Covers:
      - A normal region with both RED AND ROSE and WHITE rows
      - CHAMPAGNE (white-only region, triggers the hardcoded-red branch)
      - ALSACE ET EST (same branch as CHAMPAGNE)
    """
    rows = [
        _make_geometry_row(
            "SUD-OUEST", "RED AND ROSE", {col: 200 for col in YEAR_COLS}
        ),
        _make_geometry_row("SUD-OUEST", "WHITE", {col: 150 for col in YEAR_COLS}),
        _make_geometry_row("CHAMPAGNE", "WHITE", {col: 500 for col in YEAR_COLS}),
        _make_geometry_row("ALSACE ET EST", "WHITE", {col: 300 for col in YEAR_COLS}),
    ]
    return pd.DataFrame(rows)


# ===========================================================================
# Tests – clean_df_region_color
# ===========================================================================


class TestCleanDfRegionColor:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, single_row_df):
        result = clean_df_region_color(single_row_df)
        assert isinstance(result, pd.DataFrame)

    def test_output_has_exactly_two_columns(self, single_row_df):
        result = clean_df_region_color(single_row_df)
        assert list(result.columns) == ["Harvest", "years"]

    def test_row_count_equals_number_of_year_cols(self, single_row_df):
        result = clean_df_region_color(single_row_df)
        assert len(result) == len(YEAR_COLS)

    # --- Metadata columns are gone ---

    def test_metadata_columns_dropped(self, single_row_df):
        result = clean_df_region_color(single_row_df)
        for col in ("Region", "wine_type", "average", "latitude", "longitude"):
            assert col not in result.columns

    # --- Transpose correctness ---

    def test_years_column_matches_year_cols(self, single_row_df):
        result = clean_df_region_color(single_row_df)
        assert list(result["years"]) == YEAR_COLS

    def test_harvest_values_are_divided_by_10(self):
        """Each year value should be divided by 10 after transpose."""
        values = {col: i * 10 for i, col in enumerate(YEAR_COLS)}  # 0, 10, 20, ...
        df = pd.DataFrame([_make_geometry_row("TEST", "RED AND ROSE", values)])
        result = clean_df_region_color(df)
        expected = [i for i in range(len(YEAR_COLS))]  # 0, 1, 2, ...
        assert list(result["Harvest"]) == expected

    def test_harvest_all_zeros(self):
        values = {col: 0 for col in YEAR_COLS}
        df = pd.DataFrame([_make_geometry_row("TEST", "WHITE", values)])
        result = clean_df_region_color(df)
        assert all(result["Harvest"] == 0)

    # --- Immutability ---

    def test_does_not_mutate_input(self, single_row_df):
        original = single_row_df.copy()
        clean_df_region_color(single_row_df)
        pd.testing.assert_frame_equal(single_row_df, original)


# ===========================================================================
# Tests – create_df_region_red
# ===========================================================================


EXPECTED_HARVEST_COLUMNS = ["Harvest", "years"]


class TestCreateDfRegionRed:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert isinstance(result, pd.DataFrame)

    def test_output_columns(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(result.columns) == EXPECTED_HARVEST_COLUMNS

    # --- Normal region (goes through clean_df_region_color) ---

    def test_normal_region_harvest_divided_by_10(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        # All year values were 200 → Harvest should be 20.0 for every row
        assert all(result["Harvest"] == 20.0)

    def test_normal_region_years_match_year_cols(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(result["years"]) == YEAR_COLS

    # --- Empty regions (no red data) ---

    def test_champagne_returns_all_zeros(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        assert all(result["Harvest"] == 0)

    def test_champagne_has_correct_columns(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        assert list(result.columns) == EXPECTED_HARVEST_COLUMNS

    def test_champagne_years_match_year_cols(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        assert list(result["years"]) == YEAR_COLS
        assert len(result) == len(YEAR_COLS)

    def test_empty_region_length_driven_by_year_cols(self, full_geometry_df):
        """Passing a subset of year_cols produces a matching-length empty DataFrame."""
        subset = ["08/09", "09/10", "10/11"]
        result = create_df_region_red(full_geometry_df, "CHAMPAGNE", subset)
        assert list(result["years"]) == subset
        assert len(result) == 3
        assert all(result["Harvest"] == 0)

    def test_alsace_returns_all_zeros(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "ALSACE ET EST", YEAR_COLS)
        assert all(result["Harvest"] == 0)

    def test_alsace_years_match_year_cols(self, full_geometry_df):
        result = create_df_region_red(full_geometry_df, "ALSACE ET EST", YEAR_COLS)
        assert list(result["years"]) == YEAR_COLS

    # --- Immutability ---

    def test_does_not_mutate_input(self, full_geometry_df):
        original = full_geometry_df.copy()
        create_df_region_red(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        pd.testing.assert_frame_equal(full_geometry_df, original)


# ===========================================================================
# Tests – create_df_region_white
# ===========================================================================


class TestCreateDfRegionWhite:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, full_geometry_df):
        result = create_df_region_white(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert isinstance(result, pd.DataFrame)

    def test_output_columns(self, full_geometry_df):
        result = create_df_region_white(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(result.columns) == EXPECTED_HARVEST_COLUMNS

    # --- Normal regions (go through clean_df_region_color) ---

    def test_sud_ouest_harvest_divided_by_10(self, full_geometry_df):
        result = create_df_region_white(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        # All year values were 150 → Harvest should be 15.0
        assert all(result["Harvest"] == 15.0)

    def test_champagne_harvest_divided_by_10(self, full_geometry_df):
        result = create_df_region_white(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        # All year values were 500 → Harvest = 50.0
        assert all(result["Harvest"] == 50.0)

    def test_alsace_harvest_divided_by_10(self, full_geometry_df):
        result = create_df_region_white(full_geometry_df, "ALSACE ET EST", YEAR_COLS)
        # All year values were 300 → Harvest = 30.0
        assert all(result["Harvest"] == 30.0)

    def test_years_match_year_cols(self, full_geometry_df):
        result = create_df_region_white(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(result["years"]) == YEAR_COLS

    # --- Empty regions (no white data - edge case) ---

    def test_empty_region_returns_all_zeros(self, full_geometry_df):
        """If a region has no white wine data, return empty structure."""
        # Create a red-only region by adding a row
        df = full_geometry_df.copy()
        red_only_row = _make_geometry_row(
            "BORDEAUX", "RED AND ROSE", {col: 300 for col in YEAR_COLS}
        )
        df = pd.concat([df, pd.DataFrame([red_only_row])], ignore_index=True)

        result = create_df_region_white(df, "BORDEAUX", YEAR_COLS)
        assert all(result["Harvest"] == 0)
        assert list(result["years"]) == YEAR_COLS

    # --- Immutability ---

    def test_does_not_mutate_input(self, full_geometry_df):
        original = full_geometry_df.copy()
        create_df_region_white(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        pd.testing.assert_frame_equal(full_geometry_df, original)
