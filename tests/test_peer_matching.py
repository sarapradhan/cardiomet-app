"""
tests/test_peer_matching.py

Tests for SCORE-style peer matching in the benchmark:
  - sahc_risklens/benchmark/matching.py (pure helpers + stratified computation)
  - get_benchmark_data(..., match=True) integration and graceful fallback
  - api/routers/benchmark.py ?match=true
  - the improvement over SCORE: small-cell suppression + transparent fallback

NOTE ON SCOPE (2026-08-30). These tests previously drove the matching engine
through the "sahc" cohort, which shipped a frozen strata table. That cohort was
removed because its provenance could not be established (docs/SAHC_COHORT.md),
so no cohort ships a strata table today and every live call to
get_matched_percentiles() returns None.

The engine itself is deliberately retained — it is the seam a properly sourced
cohort plugs into — so it is still tested here, directly, against synthetic
tables in exactly the shape data/strata_tables.py would supply. That keeps the
suppression, fallback and description logic covered rather than deleting the
coverage along with the data.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app
from sahc_risklens.benchmark.matching import (
    MIN_MATCH_N,
    PatientStrata,
    age_to_band,
    describe_strata,
    resolve_patient_strata,
    stratified_from_table,
    stratum_key,
)
from sahc_risklens.benchmark.percentile import get_benchmark_data, get_matched_percentiles
from sahc_risklens.config import COHORT_NHANES, NHANES_COHORT_LABEL

client = TestClient(app)

# A 55-year-old woman, no medications.
WOMAN_55 = {
    "LDL_mgdl": 130, "HDL_mgdl": 45, "TG_mgdl": 150, "BMI_kgm2": 27,
    "age_yr": 55, "sex": "F", "chol_med": False, "bp_med": False,
    "insulin": False, "dm_pills": False,
}

STRATA_55 = PatientStrata("F", 49, False, False, False)


def _cell(n_people: int, hdl_n: int, median: float = 50.0) -> dict:
    """One strata-table entry in the shape data/strata_tables.py supplies."""
    return {
        "_n": n_people,
        "HDL": {"p10": 34.0, "p25": 41.0, "median": median,
                "p75": 59.0, "p90": 68.0, "n": hdl_n},
    }


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_age_to_band_bounds():
    assert age_to_band(18) == 19
    assert age_to_band(33) == 19
    assert age_to_band(34) == 34
    assert age_to_band(64) == 49
    assert age_to_band(65) == 65
    assert age_to_band(80) == 79
    assert age_to_band(None) is None


def test_resolve_patient_strata_diabetes_from_either_flag():
    s = resolve_patient_strata({"sex": "M", "age_yr": 40, "insulin": True})
    assert s.dm_med is True
    s2 = resolve_patient_strata({"sex": "M", "age_yr": 40, "dm_pills": True})
    assert s2.dm_med is True


def test_can_match_requires_sex_and_age():
    assert PatientStrata("F", 49, False, False, False).can_match is True
    assert PatientStrata(None, 49, False, False, False).can_match is False
    assert PatientStrata("F", None, False, False, False).can_match is False


def test_describe_strata_reads_naturally():
    s = PatientStrata("F", 49, True, False, False)
    assert describe_strata(s, "sexage") == "Women, 49–64"
    assert describe_strata(s, "full") == "Women, 49–64, on cholesterol medication"


# ---------------------------------------------------------------------------
# Matched computation, driven directly against a strata table
# ---------------------------------------------------------------------------

def test_matched_percentiles_returns_narrowest_adequate_peer_group():
    table = {
        stratum_key("F", 49, False, False, False): _cell(400, 380, median=53.0),
        stratum_key("F", 49): _cell(2000, 1900, median=50.0),
    }
    m = stratified_from_table(table, STRATA_55, ["HDL"])
    assert m is not None
    assert m["level"] == "full"          # narrowest level that clears the floor
    assert m["n"] >= MIN_MATCH_N
    assert m["per_biomarker"]["HDL"]["median"] == 53.0
    assert m["description"]


def test_falls_back_to_broader_group_when_narrow_cell_is_small():
    table = {
        stratum_key("F", 49, False, False, False): _cell(12, 12),   # below floor
        stratum_key("F", 49): _cell(2000, 1900, median=50.0),
    }
    m = stratified_from_table(table, STRATA_55, ["HDL"])
    assert m is not None
    assert m["level"] == "sexage"
    assert m["per_biomarker"]["HDL"]["median"] == 50.0


def test_small_cell_suppression_via_table():
    """A stratum below MIN_MATCH_N must not be returned from the frozen table."""
    tiny = {stratum_key("F", 49): _cell(5, 5)}
    assert stratified_from_table(tiny, STRATA_55, ["HDL"]) is None


def test_biomarker_below_floor_is_dropped_even_in_a_large_cell():
    """Cell size is not enough — each biomarker must clear the floor itself."""
    table = {stratum_key("F", 49): _cell(2000, hdl_n=9)}
    assert stratified_from_table(table, STRATA_55, ["HDL"]) is None


def test_unmatchable_patient_is_never_matched():
    assert stratified_from_table({}, PatientStrata(None, 49, False, False, False), ["HDL"]) is None
    assert stratified_from_table({}, PatientStrata("F", None, False, False, False), ["HDL"]) is None


# ---------------------------------------------------------------------------
# Integration: no cohort ships a strata table, so matching falls back cleanly
# ---------------------------------------------------------------------------

def test_no_registered_cohort_supplies_matching_today():
    """Regression guard for the 2026-08-30 removal: match=True must never error,
    and must never silently claim a match it cannot support."""
    assert get_matched_percentiles(WOMAN_55, COHORT_NHANES) is None


def test_match_true_falls_back_to_whole_cohort_and_discloses_it():
    pts = get_benchmark_data(WOMAN_55, cohort=COHORT_NHANES, match=True)
    assert pts
    for p in pts:
        assert p["matched"] is False
        assert p["match_n"] is None
        assert p["match_description"] is None


def test_match_off_is_unchanged_and_unmatched():
    for p in get_benchmark_data(WOMAN_55, cohort=COHORT_NHANES, match=False):
        assert p["matched"] is False


def test_cannot_match_without_age_or_sex():
    assert get_matched_percentiles({"LDL_mgdl": 130, "age_yr": 55}, COHORT_NHANES) is None
    pts = get_benchmark_data({"LDL_mgdl": 130}, cohort=COHORT_NHANES, match=True)
    assert pts and all(p["matched"] is False for p in pts)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def test_api_match_true_is_accepted_and_honestly_unmatched():
    r = client.post("/api/v1/benchmark?match=true", json=WOMAN_55)
    assert r.status_code == 200
    body = r.json()
    assert body["matched"] is False
    assert body["match_description"] is None
    hdl = next(p for p in body["benchmark_data"] if p["biomarker"] == "HDL")
    assert hdl["matched"] is False and hdl["match_n"] is None
    assert hdl["cohort_label"] == NHANES_COHORT_LABEL


def test_api_match_default_off():
    r = client.post("/api/v1/benchmark", json=WOMAN_55)
    body = r.json()
    assert body["matched"] is False
    assert body["match_description"] is None
