"""
tests/test_peer_matching.py

Tests for SCORE-style peer matching in the benchmark:
  - sahc_risklens/benchmark/matching.py (pure helpers + stratified computation)
  - get_benchmark_data(..., match=True) integration
  - api/routers/benchmark.py ?match=true
  - the improvement over SCORE: small-cell suppression + transparent fallback

Default (match=False) behavior is covered by test_percentile.py / test_sahc_cohort.py
and must remain unchanged.
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
)
from sahc_risklens.benchmark.percentile import get_benchmark_data, get_matched_percentiles
from sahc_risklens.config import COHORT_NHANES, COHORT_SAHC, SAHC_COHORT_LABEL

client = TestClient(app)

# A 55-year-old woman, no medications — a well-populated SAHC stratum.
WOMAN_55 = {
    "LDL_mgdl": 130, "HDL_mgdl": 45, "TG_mgdl": 150, "BMI_kgm2": 27,
    "age_yr": 55, "sex": "F", "chol_med": False, "bp_med": False,
    "insulin": False, "dm_pills": False,
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
# Matched computation
# ---------------------------------------------------------------------------

def test_matched_percentiles_returns_peer_group():
    m = get_matched_percentiles(WOMAN_55, COHORT_SAHC)
    assert m is not None
    assert m["level"] in ("full", "sexage")
    assert m["n"] >= MIN_MATCH_N
    assert "HDL" in m["per_biomarker"]


def test_matching_changes_the_distribution():
    """The whole point: matched peers differ from the whole cohort."""
    whole = {p["biomarker"]: p for p in get_benchmark_data(WOMAN_55, cohort=COHORT_SAHC)}
    matched = {p["biomarker"]: p for p in get_benchmark_data(WOMAN_55, cohort=COHORT_SAHC, match=True)}
    # HDL median for women 49-64 is higher than the whole-cohort median.
    assert matched["HDL"]["matched"] is True
    assert matched["HDL"]["cohort_median"] != whole["HDL"]["cohort_median"]
    assert matched["HDL"]["match_n"] is not None
    assert matched["HDL"]["match_description"]


def test_match_off_is_unchanged_and_unmatched():
    for p in get_benchmark_data(WOMAN_55, cohort=COHORT_SAHC, match=False):
        assert p["matched"] is False
        assert p["match_n"] is None
        assert p["match_description"] is None


def test_cannot_match_without_age_or_sex():
    assert get_matched_percentiles({"LDL_mgdl": 130, "age_yr": 55}, COHORT_SAHC) is None
    # match=True but unmatchable -> falls back to whole cohort, all unmatched
    pts = get_benchmark_data({"LDL_mgdl": 130}, cohort=COHORT_SAHC, match=True)
    assert pts and all(p["matched"] is False for p in pts)


def test_nhanes_matching_falls_back_gracefully():
    """NHANES has no stratified source; match=True must not error, just fall back."""
    assert get_matched_percentiles(WOMAN_55, COHORT_NHANES) is None
    pts = get_benchmark_data(WOMAN_55, cohort=COHORT_NHANES, match=True)
    assert pts and all(p["matched"] is False for p in pts)


def test_small_cell_suppression_via_table():
    """A stratum below MIN_MATCH_N must not be returned from the frozen table."""
    tiny = {"sex=F|age=49|chol=*|bp=*|dm=*": {"_n": 5, "HDL": {"p10": 1, "p25": 2,
            "median": 3, "p75": 4, "p90": 5, "n": 5}}}
    s = PatientStrata("F", 49, False, False, False)
    assert stratified_from_table(tiny, s, ["HDL"]) is None


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def test_api_match_true_reports_matched():
    r = client.post("/api/v1/benchmark?cohort=sahc&match=true", json=WOMAN_55)
    assert r.status_code == 200
    body = r.json()
    assert body["matched"] is True
    assert body["match_description"]
    hdl = next(p for p in body["benchmark_data"] if p["biomarker"] == "HDL")
    assert hdl["matched"] is True and hdl["match_n"]
    # Label safety still holds under matching.
    assert hdl["cohort_label"] == SAHC_COHORT_LABEL


def test_api_match_default_off():
    r = client.post("/api/v1/benchmark?cohort=sahc", json=WOMAN_55)
    body = r.json()
    assert body["matched"] is False
    assert body["match_description"] is None
