import pandas as pd
import pytest
from shapely.geometry import Point, mapping

from src.algorithms import add_basic_stats, add_geometry

# ---------------------------------------------------------------------------
# Paste (or import) the functions under test here so the file is self-contained.
# Replace this block with: from your_module import add_basic_stats, add_geometry
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


def _make_year_row(value: float) -> dict:
    """Return a dict mapping every year column to the same value."""
    return {col: value for col in YEAR_COLS}


@pytest.fixture
def raw_wine_df() -> pd.DataFrame:
    """Minimal raw wine DataFrame mimicking the real CSV structure.

    Layout chosen to exercise every branch:
      - Two regions (SUD-OUEST, VAL DE LOIRE)
      - One AOC marked as (subset) → must be filtered out by add_geometry
      - One row with a differing year value → makes min ≠ max
    """
    rows = [
        {
            "wine_basin": "SUD-OUEST",
            "AOC": "BORDEAUX MOUSSEUX",
            "wine_type": "RED",
            **_make_year_row(100),
        },
        {
            "wine_basin": "SUD-OUEST",
            "AOC": "BORDEAUX MOUSSEUX (subset)",
            "wine_type": "RED",
            **_make_year_row(40),
        },
        {
            "wine_basin": "SUD-OUEST",
            "AOC": "CAHORS",
            "wine_type": "RED",
            **{**_make_year_row(200), "08/09": 50},
        },
        {
            "wine_basin": "VAL DE LOIRE",
            "AOC": "CREMANT DE LOIRE",
            "wine_type": "WHITE",
            **_make_year_row(300),
        },
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def stats_df(raw_wine_df) -> pd.DataFrame:
    """Pre-computed stats DataFrame (output of add_basic_stats)."""
    return add_basic_stats(raw_wine_df, YEAR_COLS)


def _point_in_3857(lon: float, lat: float) -> dict:
    """Create a GeoJSON Feature with a point in EPSG:3857 (Web Mercator)."""
    # Convert lon/lat (4326) -> approximate 3857 for the fixture
    import math

    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return {
        "type": "Feature",
        "properties": {"Bassin": lon},  # placeholder; overwritten below
        "geometry": mapping(Point(x, y)),
    }


@pytest.fixture
def geometry_features() -> list:
    """GeoJSON feature list matching the regions in raw_wine_df."""
    features = []
    for bassin, lon, lat in [
        ("SUD-OUEST", -0.58, 44.84),
        ("VAL DE LOIRE", -1.55, 47.39),
    ]:
        feat = _point_in_3857(lon, lat)
        feat["properties"]["Bassin"] = bassin
        features.append(feat)
    return features


# ===========================================================================
# Tests – add_basic_stats
# ===========================================================================


class TestAddBasicStats:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        assert isinstance(result, pd.DataFrame)

    def test_new_columns_present(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        for col in ("min", "max", "average"):
            assert col in result.columns

    def test_row_count_unchanged(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        assert len(result) == len(raw_wine_df)

    def test_wine_basin_renamed_to_region(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        assert "Region" in result.columns
        assert "wine_basin" not in result.columns

    # --- Correctness of computed stats ---

    def test_min_values(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        # Row 0: all 100 → min 100
        assert result.loc[0, "min"] == 100
        # Row 2: one value is 50, rest 200 → min 50
        assert result.loc[2, "min"] == 50

    def test_max_values(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        # Row 2: one value is 50, rest 200 → max 200
        assert result.loc[2, "max"] == 200
        # Row 3: all 300 → max 300
        assert result.loc[3, "max"] == 300

    def test_average_values(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        # Row 0: all 100 → average 100.0
        assert result.loc[0, "average"] == 100.0
        # Row 2: (50 + 200*10) / 11 ≈ 186.36
        expected = round((50 + 200 * 10) / 11, 2)
        assert result.loc[2, "average"] == expected

    def test_average_is_rounded_to_two_decimals(self, raw_wine_df):
        result = add_basic_stats(raw_wine_df, YEAR_COLS)
        for val in result["average"]:
            # Check that at most 2 decimal places
            assert round(val, 2) == val

    # --- Immutability ---

    def test_does_not_mutate_input(self, raw_wine_df):
        original = raw_wine_df.copy()
        add_basic_stats(raw_wine_df, YEAR_COLS)
        pd.testing.assert_frame_equal(raw_wine_df, original)

    # --- Edge cases ---

    def test_single_row(self):
        row = {
            "wine_basin": "Test",
            "AOC": "X",
            "wine_type": "Red",
            **_make_year_row(42),
        }
        df = pd.DataFrame([row])
        result = add_basic_stats(df, YEAR_COLS)
        assert result.loc[0, "min"] == 42
        assert result.loc[0, "max"] == 42
        assert result.loc[0, "average"] == 42.0

    def test_all_zeros(self):
        row = {
            "wine_basin": "Zero",
            "AOC": "Z",
            "wine_type": "White",
            **_make_year_row(0),
        }
        df = pd.DataFrame([row])
        result = add_basic_stats(df, YEAR_COLS)
        assert result.loc[0, "min"] == 0
        assert result.loc[0, "max"] == 0
        assert result.loc[0, "average"] == 0.0

    def test_negative_values(self):
        """Stats should work even with negative numbers (hypothetical corrections)."""
        years = {col: -10 for col in YEAR_COLS}
        years["08/09"] = -50
        row = {"wine_basin": "Neg", "AOC": "N", "wine_type": "Red", **years}
        df = pd.DataFrame([row])
        result = add_basic_stats(df, YEAR_COLS)
        assert result.loc[0, "min"] == -50
        assert result.loc[0, "max"] == -10

    # --- year_cols parameter actually controls which columns are used ---

    def test_subset_of_year_cols(self):
        """Passing only a subset of year columns should compute stats over that subset
        only."""
        row = {
            "wine_basin": "Sub",
            "AOC": "S",
            "wine_type": "Red",
            **_make_year_row(100),
        }
        row["08/09"] = 10  # outlier, but only matters if 08/09 is in year_cols
        df = pd.DataFrame([row])

        subset = ["09/10", "10/11"]  # both are 100, 08/09 excluded
        result = add_basic_stats(df, subset)
        assert result.loc[0, "min"] == 100
        assert result.loc[0, "max"] == 100
        assert result.loc[0, "average"] == 100.0

    def test_single_year_col(self):
        """A single-element year_cols list should still work."""
        row = {
            "wine_basin": "One",
            "AOC": "O",
            "wine_type": "Red",
            **_make_year_row(77),
        }
        df = pd.DataFrame([row])
        result = add_basic_stats(df, ["08/09"])
        assert result.loc[0, "min"] == 77
        assert result.loc[0, "max"] == 77
        assert result.loc[0, "average"] == 77.0


# ===========================================================================
# Tests – add_geometry
# ===========================================================================


class TestAddGeometry:
    # --- Output shape & columns ---

    def test_returns_dataframe(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert isinstance(result, pd.DataFrame)

    def test_has_latitude_and_longitude(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert "latitude" in result.columns
        assert "longitude" in result.columns

    def test_bassin_column_dropped(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert "Bassin" not in result.columns

    def test_aoc_column_dropped(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert "AOC" not in result.columns

    def test_min_max_columns_dropped(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert "min" not in result.columns
        assert "max" not in result.columns

    # --- Subset filtering ---

    def test_subset_rows_are_removed(self, stats_df, geometry_features):
        """Rows whose AOC contains '(subset)' must not contribute to the output."""
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        sud_ouest_red = result[
            (result["Region"] == "SUD-OUEST") & (result["wine_type"] == "RED")
        ]
        assert len(sud_ouest_red) == 1
        # Non-subset SUD-OUEST RED rows: row 0 (all 100) + row 2 (08/09=50, rest 200)
        expected_08_09 = 100 + 50  # 150
        assert sud_ouest_red.iloc[0]["08/09"] == expected_08_09

    # --- Groupby aggregation ---

    def test_groupby_sums_year_columns(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        # VAL DE LOIRE / WHITE: only CREMANT DE LOIRE (all 300)
        loire_white = result[
            (result["Region"] == "VAL DE LOIRE") & (result["wine_type"] == "WHITE")
        ]
        assert len(loire_white) == 1
        for col in YEAR_COLS:
            assert loire_white.iloc[0][col] == 300

    # --- Average is now correctly recalculated from summed year columns ---

    def test_average_is_recalculated_after_groupby(self, stats_df, geometry_features):
        """
        SUD-OUEST/RED after dropping (subset), two AOCs are summed:
          row 0: all years = 100
          row 2: 08/09 = 50, rest = 200

        Summed year columns: 08/09 = 150, rest = 300
        Correct average = mean(150, 300, 300, ..., 300) = (150 + 300*10) / 11 ≈ 286.36
        """
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        sud_ouest_red = result[
            (result["Region"] == "SUD-OUEST") & (result["wine_type"] == "RED")
        ]
        expected_average = round((150 + 300 * 10) / 11, 2)  # 286.36
        assert sud_ouest_red.iloc[0]["average"] == expected_average

    def test_average_recalculation_single_aoc(self, stats_df, geometry_features):
        """Single-AOC group: average should equal the mean of that row's year cols."""
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        loire_white = result[
            (result["Region"] == "VAL DE LOIRE") & (result["wine_type"] == "WHITE")
        ]
        # All years are 300 → average = 300.0
        assert loire_white.iloc[0]["average"] == 300.0

    # --- Sorting ---

    def test_sorted_by_average_descending(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        averages = result["average"].tolist()
        assert averages == sorted(averages, reverse=True)

    # --- Coordinate sanity ---

    def test_latitude_in_valid_range(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert result["latitude"].between(-90, 90).all()

    def test_longitude_in_valid_range(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        assert result["longitude"].between(-180, 180).all()

    def test_sud_ouest_coordinates_approx(self, stats_df, geometry_features):
        """SUD-OUEST should be roughly at lon ≈ -0.58, lat ≈ 44.84."""
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        sud_ouest = result[result["Region"] == "SUD-OUEST"].iloc[0]
        assert sud_ouest["longitude"] == pytest.approx(-0.58, abs=0.1)
        assert sud_ouest["latitude"] == pytest.approx(44.84, abs=0.1)

    # --- Immutability ---

    def test_does_not_mutate_input(self, stats_df, geometry_features):
        original = stats_df.copy()
        add_geometry(stats_df, geometry_features, YEAR_COLS)
        pd.testing.assert_frame_equal(stats_df, original)

    # --- Index is clean ---

    def test_index_is_reset(self, stats_df, geometry_features):
        result = add_geometry(stats_df, geometry_features, YEAR_COLS)
        expected_index = list(range(len(result)))
        assert list(result.index) == expected_index

    # --- year_cols parameter actually controls which columns are used ---

    def test_average_respects_year_cols_subset(self, geometry_features):
        """Passing a subset of year_cols should compute the average over only those."""
        subset = ["08/09", "09/10"]
        rows = [
            {
                "wine_basin": "SUD-OUEST",
                "AOC": "CAHORS",
                "wine_type": "RED",
                **_make_year_row(100),
                "08/09": 0,
                "09/10": 0,
            },
            {
                "wine_basin": "VAL DE LOIRE",
                "AOC": "CREMANT DE LOIRE",
                "wine_type": "WHITE",
                **_make_year_row(200),
            },
        ]
        df = pd.DataFrame(rows)
        stats = add_basic_stats(df, subset)
        result = add_geometry(stats, geometry_features, subset)

        # SUD-OUEST/RED: 08/09=0, 09/10=0 → average over subset = 0.0
        sud_ouest = result[result["Region"] == "SUD-OUEST"].iloc[0]
        assert sud_ouest["average"] == 0.0

        # VAL DE LOIRE/WHITE: 08/09=200, 09/10=200 → average over subset = 200.0
        val_de_loire = result[result["Region"] == "VAL DE LOIRE"].iloc[0]
        assert val_de_loire["average"] == 200.0
