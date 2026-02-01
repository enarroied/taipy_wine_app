import pandas as pd
import pytest

from src.algorithms import clean_df_region_color, create_df_region

# ---------------------------------------------------------------------------
# Paste (or import) the functions under test here so the file is self-contained.
# Replace this block with:
#   from your_module import clean_df_region_color, create_df_region
# ---------------------------------------------------------------------------

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
# Tests – create_df_region
# ===========================================================================


class TestCreateDfRegion:
    # --- Return type ---

    def test_returns_tuple_of_two_dataframes(self, full_geometry_df):
        result = create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], pd.DataFrame)

    # --- Normal region (both colours go through clean_df_region_color) ---

    def test_normal_region_red_has_correct_columns(self, full_geometry_df):
        red, _ = create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(red.columns) == ["Harvest", "years"]

    def test_normal_region_white_has_correct_columns(self, full_geometry_df):
        _, white = create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(white.columns) == ["Harvest", "years"]

    def test_normal_region_red_harvest_divided_by_10(self, full_geometry_df):
        red, _ = create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        # All year values were 200 → Harvest should be 20.0 for every row
        assert all(red["Harvest"] == 20.0)

    def test_normal_region_white_harvest_divided_by_10(self, full_geometry_df):
        _, white = create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        # All year values were 150 → Harvest should be 15.0
        assert all(white["Harvest"] == 15.0)

    def test_normal_region_years_match_year_cols(self, full_geometry_df):
        red, white = create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        assert list(red["years"]) == YEAR_COLS
        assert list(white["years"]) == YEAR_COLS

    # --- White-only regions (CHAMPAGNE / ALSACE ET EST) ---
    # These trigger the fallback-red branch instead of clean_df_region_color.

    def test_champagne_red_is_all_zeros(self, full_geometry_df):
        red, _ = create_df_region(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        assert all(red["Harvest"] == 0)

    def test_champagne_red_has_correct_columns(self, full_geometry_df):
        red, _ = create_df_region(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        assert list(red.columns) == ["Harvest", "years"]

    def test_champagne_red_years_match_year_cols(self, full_geometry_df):
        """Fallback red DataFrame must cover exactly the same years as year_cols."""
        red, _ = create_df_region(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        assert list(red["years"]) == YEAR_COLS
        assert len(red) == len(YEAR_COLS)

    def test_champagne_red_length_driven_by_year_cols(self, full_geometry_df):
        """Passing a subset of year_cols should produce a matching-length fallback."""
        subset = ["08/09", "09/10", "10/11"]
        red, _ = create_df_region(full_geometry_df, "CHAMPAGNE", subset)
        assert list(red["years"]) == subset
        assert len(red) == 3
        assert all(red["Harvest"] == 0)

    def test_champagne_white_is_cleaned_normally(self, full_geometry_df):
        _, white = create_df_region(full_geometry_df, "CHAMPAGNE", YEAR_COLS)
        # All year values were 500 → Harvest = 50.0
        assert list(white.columns) == ["Harvest", "years"]
        assert all(white["Harvest"] == 50.0)

    def test_alsace_red_is_all_zeros(self, full_geometry_df):
        red, _ = create_df_region(full_geometry_df, "ALSACE ET EST", YEAR_COLS)
        assert all(red["Harvest"] == 0)

    def test_alsace_red_years_match_year_cols(self, full_geometry_df):
        red, _ = create_df_region(full_geometry_df, "ALSACE ET EST", YEAR_COLS)
        assert list(red["years"]) == YEAR_COLS

    def test_alsace_white_is_cleaned_normally(self, full_geometry_df):
        _, white = create_df_region(full_geometry_df, "ALSACE ET EST", YEAR_COLS)
        # All year values were 300 → Harvest = 30.0
        assert all(white["Harvest"] == 30.0)

    # --- Immutability ---

    def test_does_not_mutate_input(self, full_geometry_df):
        original = full_geometry_df.copy()
        create_df_region(full_geometry_df, "SUD-OUEST", YEAR_COLS)
        pd.testing.assert_frame_equal(full_geometry_df, original)
