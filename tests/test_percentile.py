"""
tests/test_percentile.py

Tests for sahc_risklens/benchmark/percentile.py and sahc_risklens/data/demo_cohort.py.

Benchmark output is verified for structure and ordering regardless of data source.
Demo-cohort values are checked for determinism and internal consistency
(p10 <= p25 <= median <= p75 <= p90).
"""
from __future__ import annotations

from sahc_risklens.benchmark.percentile import (
    get_benchmark_data,
    get_cohort_percentiles,
    percentile_rank,
)
from sahc_risklens.data.demo_cohort import demo_biomarker_keys, get_demo_percentiles

_EXPECTED_KEYS = ["LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP", "BMI"]


# ---------------------------------------------------------------------------
# Demo cohort
# ---------------------------------------------------------------------------

def test_demo_cohort_covers_all_biomarkers():
    assert demo_biomarker_keys() == _EXPECTED_KEYS


def test_demo_percentiles_are_monotonic():
    for key, stats in get_demo_percentiles().items():
        assert stats["p10"] <= stats["p25"] <= stats["median"] <= stats["p75"] <= stats["p90"], key


def test_demo_percentiles_have_sample_sizes():
    for key, stats in get_demo_percentiles().items():
        assert stats["n"] > 0, key


def test_demo_percentiles_deterministic():
    """Two calls return identical values (frozen table, no randomness)."""
    assert get_demo_percentiles() == get_demo_percentiles()


def test_demo_percentiles_return_copy():
    """Mutating the returned dict must not corrupt the source table."""
    a = get_demo_percentiles()
    a["LDL"]["median"] = -999
    b = get_demo_percentiles()
    assert b["LDL"]["median"] != -999


# ---------------------------------------------------------------------------
# Benchmark output structure
# ---------------------------------------------------------------------------

def test_get_cohort_percentiles_has_required_fields():
    table = get_cohort_percentiles()
    for key in _EXPECTED_KEYS:
        assert key in table
        for field in ["p10", "p25", "median", "p75", "p90", "n"]:
            assert field in table[key], f"{key} missing {field}"


def test_benchmark_data_shape_and_order():
    data = {
        "LDL_mgdl": 100, "HDL_mgdl": 55, "TG_mgdl": 120, "TC_mgdl": 180,
        "HbA1c_pct": 5.5, "FPG_mgdl": 95, "SBP_mmhg": 118, "DBP_mmhg": 76,
        "BMI_kgm2": 24.0,
    }
    points = get_benchmark_data(data)
    assert [p["biomarker"] for p in points] == _EXPECTED_KEYS
    for p in points:
        for field in ["patient_value", "cohort_p10", "cohort_p25", "cohort_median",
                      "cohort_p75", "cohort_p90", "cohort_label", "cohort_n"]:
            assert field in p


def test_benchmark_cohort_label_constant():
    points = get_benchmark_data({"LDL_mgdl": 100})
    for p in points:
        assert p["cohort_label"] == "NHANES Non-Hispanic Asian"


def test_benchmark_patient_value_passthrough():
    points = get_benchmark_data({"LDL_mgdl": 142})
    ldl = next(p for p in points if p["biomarker"] == "LDL")
    assert ldl["patient_value"] == 142


def test_benchmark_handles_missing_patient_value():
    """Benchmark distribution is still returned when the patient value is None."""
    points = get_benchmark_data({"LDL_mgdl": None})
    ldl = next(p for p in points if p["biomarker"] == "LDL")
    assert ldl["patient_value"] is None
    assert ldl["cohort_median"] > 0  # distribution still present


def test_benchmark_monotonic_percentiles():
    for p in get_benchmark_data({"LDL_mgdl": 100}):
        assert (p["cohort_p10"] <= p["cohort_p25"] <= p["cohort_median"]
                <= p["cohort_p75"] <= p["cohort_p90"])


# ---------------------------------------------------------------------------
# percentile_rank
# ---------------------------------------------------------------------------

def test_percentile_rank_at_median():
    median_ldl = get_cohort_percentiles()["LDL"]["median"]
    assert percentile_rank(median_ldl, "LDL") == 50.0


def test_percentile_rank_below_p10_clamps():
    assert percentile_rank(-100, "LDL") == 10.0


def test_percentile_rank_above_p90_clamps():
    assert percentile_rank(10_000, "LDL") == 90.0


def test_percentile_rank_unknown_biomarker_none():
    assert percentile_rank(100, "NOT_A_BIOMARKER") is None


def test_percentile_rank_interpolates_between_anchors():
    stats = get_cohort_percentiles()["LDL"]
    midpoint = (stats["p25"] + stats["median"]) / 2
    rank = percentile_rank(midpoint, "LDL")
    assert 25.0 <= rank <= 50.0
