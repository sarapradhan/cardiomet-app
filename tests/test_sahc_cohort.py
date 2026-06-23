"""
tests/test_sahc_cohort.py

Tests for the South Asian Heart Center (SAHC) selectable benchmark cohort:
  - sahc_risklens/data/sahc_demo_cohort.py (frozen aggregate percentiles)
  - sahc_risklens/benchmark/percentile.py cohort parameterization
  - api/routers/benchmark.py ?cohort= selection
  - cohort label safety (NHANES and SAHC labels are never crossed)

These complement tests/test_percentile.py, which covers the default (NHANES) path.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app
from sahc_risklens.benchmark.percentile import (
    SUPPORTED_COHORTS,
    get_benchmark_data,
    get_cohort_percentiles,
    percentile_rank,
)
from sahc_risklens.config import (
    COHORT_NHANES,
    COHORT_SAHC,
    NHANES_COHORT_LABEL,
    SAHC_COHORT_LABEL,
)
from sahc_risklens.data.sahc_demo_cohort import demo_biomarker_keys, get_demo_percentiles

_EXPECTED_KEYS = ["LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP", "BMI"]

client = TestClient(app)


# ---------------------------------------------------------------------------
# Frozen SAHC demo cohort
# ---------------------------------------------------------------------------

def test_sahc_demo_cohort_covers_all_biomarkers():
    assert demo_biomarker_keys() == _EXPECTED_KEYS


def test_sahc_demo_percentiles_are_monotonic():
    for key, stats in get_demo_percentiles().items():
        assert stats["p10"] <= stats["p25"] <= stats["median"] <= stats["p75"] <= stats["p90"], key


def test_sahc_demo_percentiles_have_sample_sizes():
    for key, stats in get_demo_percentiles().items():
        assert stats["n"] > 0, key


def test_sahc_demo_percentiles_return_copy():
    a = get_demo_percentiles()
    a["LDL"]["median"] = -999
    assert get_demo_percentiles()["LDL"]["median"] != -999


# ---------------------------------------------------------------------------
# Cohort parameterization in the benchmark layer
# ---------------------------------------------------------------------------

def test_supported_cohorts_are_both_registered():
    assert set(SUPPORTED_COHORTS) == {COHORT_NHANES, COHORT_SAHC}


def test_get_cohort_percentiles_sahc_has_required_fields():
    table = get_cohort_percentiles(COHORT_SAHC)
    for key in _EXPECTED_KEYS:
        assert key in table
        for field in ["p10", "p25", "median", "p75", "p90", "n"]:
            assert field in table[key], f"{key} missing {field}"


def test_sahc_and_nhanes_cohorts_are_distinct():
    """The two cohorts must not be the same distribution (different populations)."""
    nhanes = get_cohort_percentiles(COHORT_NHANES)
    sahc = get_cohort_percentiles(COHORT_SAHC)
    # At least HDL/TG medians differ (the documented South Asian dyslipidemia pattern).
    assert sahc["HDL"]["median"] != nhanes["HDL"]["median"]
    assert sahc["TG"]["median"] != nhanes["TG"]["median"]


def test_benchmark_data_sahc_label():
    points = get_benchmark_data({"LDL_mgdl": 120}, cohort=COHORT_SAHC)
    assert points  # non-empty
    for p in points:
        assert p["cohort_label"] == SAHC_COHORT_LABEL


def test_benchmark_data_default_is_nhanes():
    """Calling without a cohort preserves the original NHANES contract."""
    for p in get_benchmark_data({"LDL_mgdl": 120}):
        assert p["cohort_label"] == NHANES_COHORT_LABEL


def test_unknown_cohort_raises():
    with pytest.raises(ValueError):
        get_cohort_percentiles("not_a_cohort")
    with pytest.raises(ValueError):
        get_benchmark_data({"LDL_mgdl": 100}, cohort="not_a_cohort")


def test_percentile_rank_respects_cohort():
    rank = percentile_rank(get_cohort_percentiles(COHORT_SAHC)["HDL"]["median"], "HDL", cohort=COHORT_SAHC)
    assert rank == 50.0


# ---------------------------------------------------------------------------
# Label-safety invariant: the two cohort labels are never crossed
# ---------------------------------------------------------------------------

def test_nhanes_cohort_never_emits_sahc_label():
    for p in get_benchmark_data({"LDL_mgdl": 100}, cohort=COHORT_NHANES):
        assert p["cohort_label"] != SAHC_COHORT_LABEL


def test_sahc_cohort_never_emits_nhanes_label():
    for p in get_benchmark_data({"LDL_mgdl": 100}, cohort=COHORT_SAHC):
        assert p["cohort_label"] != NHANES_COHORT_LABEL


def test_sahc_label_is_not_bare_south_asian():
    """Guard the CLAUDE.md intent: the SAHC label is a proper-noun cohort name,
    not the bare phrase 'South Asian' that the NHANES proxy must never use."""
    assert SAHC_COHORT_LABEL != "South Asian"
    assert "Heart Center" in SAHC_COHORT_LABEL


# ---------------------------------------------------------------------------
# API surface
# ---------------------------------------------------------------------------

def test_api_default_cohort_is_nhanes():
    r = client.post("/api/v1/benchmark", json={"LDL_mgdl": 142})
    assert r.status_code == 200
    body = r.json()
    assert body["cohort"] == COHORT_NHANES
    assert body["cohort_label"] == NHANES_COHORT_LABEL


def test_api_sahc_cohort_selected():
    r = client.post("/api/v1/benchmark?cohort=sahc", json={"LDL_mgdl": 142})
    assert r.status_code == 200
    body = r.json()
    assert body["cohort"] == COHORT_SAHC
    assert body["cohort_label"] == SAHC_COHORT_LABEL
    assert all(p["cohort_label"] == SAHC_COHORT_LABEL for p in body["benchmark_data"])


def test_api_unknown_cohort_rejected():
    r = client.post("/api/v1/benchmark?cohort=bogus", json={"LDL_mgdl": 142})
    assert r.status_code == 422
