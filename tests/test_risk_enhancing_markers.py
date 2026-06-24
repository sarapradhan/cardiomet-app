"""
tests/test_risk_enhancing_markers.py

Tests for the advanced lipid risk-enhancing markers (ApoB, Lp(a)) —
classification-only, not cohort-benchmarked. See
sahc_risklens/clinical/thresholds.classify_risk_enhancing_markers.

Invariants:
  - they classify against guideline cut-points (no percentile/benchmark),
  - they are NOT part of the core 9 benchmarked biomarkers,
  - blank markers are omitted (NOT reported as missing_biomarkers),
  - elevated Lp(a) adds a South Asian context item.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app
from sahc_risklens.clinical.thresholds import (
    classify_all_biomarkers,
    classify_risk_enhancing_markers,
)

client = TestClient(app)


def test_apob_classification_bands():
    assert classify_risk_enhancing_markers({"ApoB_mgdl": 80})[0]["category"] == "Within range"
    assert classify_risk_enhancing_markers({"ApoB_mgdl": 100})[0]["category"] == "Borderline"
    assert classify_risk_enhancing_markers({"ApoB_mgdl": 140})[0]["category"] == "High (risk-enhancing)"


def test_lpa_classification_bands():
    assert classify_risk_enhancing_markers({"Lpa_mgdl": 20})[0]["category"] == "Within range"
    assert classify_risk_enhancing_markers({"Lpa_mgdl": 40})[0]["category"] == "Borderline"
    assert classify_risk_enhancing_markers({"Lpa_mgdl": 60})[0]["category"] == "High (risk-enhancing)"


def test_blank_markers_omitted_not_missing():
    """Unsupplied advanced markers produce no rows and are not 'missing'."""
    assert classify_risk_enhancing_markers({"LDL_mgdl": 100}) == []
    body = client.post("/api/v1/benchmark", json={"LDL_mgdl": 100}).json()
    assert body["risk_enhancing_markers"] == []
    assert not any("ApoB" in m or "Lpa" in m for m in body["missing_biomarkers"])


def test_not_part_of_core_nine():
    """Adding advanced markers must not change the core benchmarked panel."""
    results = classify_all_biomarkers({"ApoB_mgdl": 100, "Lpa_mgdl": 60})
    assert len(results) == 9
    assert "ApoB" not in {r["biomarker"] for r in results}


def test_apob_has_medication_note_when_on_chol_med():
    r = classify_risk_enhancing_markers({"ApoB_mgdl": 100, "chol_med": True})[0]
    assert r["note"] is not None
    # Lp(a) is not statin-modifiable -> no medication note even on chol med.
    lpa = classify_risk_enhancing_markers({"Lpa_mgdl": 60, "chol_med": True})[0]
    assert lpa["note"] is None


def test_not_benchmarked_no_percentile_fields():
    r = classify_risk_enhancing_markers({"ApoB_mgdl": 140})[0]
    assert "cohort_median" not in r and "cohort_p50" not in r


def test_elevated_lpa_adds_south_asian_context():
    body = client.post("/api/v1/benchmark", json={
        "Lpa_mgdl": 60, "south_asian": True}).json()
    factors = [i["factor"] for i in body["south_asian_context"]]
    assert any("Lipoprotein(a)" in f for f in factors)


def test_normal_lpa_no_extra_context():
    body = client.post("/api/v1/benchmark", json={
        "Lpa_mgdl": 20, "south_asian": True}).json()
    factors = [i["factor"] for i in body["south_asian_context"]]
    assert not any("Lipoprotein(a)" in f for f in factors)


def test_api_round_trips_advanced_markers():
    body = client.post("/api/v1/benchmark", json={
        "ApoB_mgdl": 135, "Lpa_mgdl": 55}).json()
    labels = {m["biomarker"] for m in body["risk_enhancing_markers"]}
    assert labels == {"ApoB", "Lp(a)"}
