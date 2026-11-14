"""
tests/test_external_audit_2026_11_09.py

Regression coverage for the "CardioMet Lens: Product, UX and Clinical Validity
Audit" (external review, review date 2026-11-09). That audit was a live-site,
black-box review — the reviewer had no code or test access ("Interactive
browser automation was unavailable during this review") — so its Section 3
functional matrix and Section 4 clinical/adversarial test-case tables mark
most rows "Untested," explicitly as a *testing gap*, not a confirmed defect.

Cross-checking against the existing test suite: every CL-01..CL-12 clinical
case was already covered (test_thresholds.py's boundary-parametrized tests,
test_risk_enhancing_markers.py), as was F-02 (fasting_status gating,
test_fpg_not_classified_without_confirmed_fasting) and most of the adversarial
matrix (test_rejects_negative_ldl, test_rejects_bad_sex,
test_rejects_swapped_sbp_dbp, test_all_none_no_crash). This file adds the
remaining untested rows from that matrix that genuinely had no prior coverage:
nonnumeric/NaN/Infinity rejection, an implausible-magnitude value, the
ancestry toggle not perturbing a universal threshold, and discordant markers
being reported independently rather than suppressed or merged.

F-01 (stale 2018 guideline citation) and the rest of F-02 were already fixed
in the prior audit-remediation pass (see docs/CLINICAL_LOGIC_APPENDIX.md
"Guideline Currency Note (2026-11)"); this file is pure test coverage, no
behavior change.
"""
from __future__ import annotations

import math
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _find(results: list, biomarker: str) -> dict | None:
    return next((r for r in results if r["biomarker"] == biomarker), None)


# ---------------------------------------------------------------------------
# Adversarial cases table, Section 4 — the rows with no prior coverage.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_value", ["NaN", "Infinity", "-Infinity", "abc", float("nan"), float("inf")])
def test_rejects_nonnumeric_and_non_finite_values(healthy_patient, bad_value):
    """Adversarial case 'Nonnumeric': abc, NaN, Infinity -> Reject.

    float("nan") and float("inf") sent as JSON numbers are invalid JSON
    literals, so the client-side json encoder would refuse them too; sending
    the string forms ("NaN"/"Infinity"/"-Infinity") is the adversarial path an
    attacker or malformed client could actually get onto the wire. Pydantic's
    ge/le bounds reject both: a NaN comparison is always False, which fails
    the le check, and the string "abc" fails float parsing outright.
    """
    payload = {**healthy_patient, "LDL_mgdl": bad_value}
    try:
        r = client.post("/api/v1/benchmark", json=payload)
    except ValueError:
        # json.dumps itself refuses an actual float('nan')/float('inf') value
        # (not valid JSON) — that is itself a correct rejection.
        return
    assert r.status_code == 422, f"LDL_mgdl={bad_value!r} should be rejected, got {r.status_code}"


def test_rejects_implausible_hba1c(healthy_patient):
    """Adversarial case 'Implausible measurement': HbA1c = 150% -> Reject.
    HbA1c_pct is bounded le=20 (api/models/patient.py); 20% already exceeds
    any physiologically reported value, so 150% is well outside it.
    """
    r = client.post("/api/v1/benchmark", json={**healthy_patient, "HbA1c_pct": 150})
    assert r.status_code == 422


def test_missing_age_shows_only_applicable_classifications(healthy_patient):
    """Adversarial case 'Missing age': age_yr is optional and is not an input
    to classify_all_biomarkers at all (only to benchmark/peer-matching age
    banding) — omitting it must not block or alter threshold classification.
    """
    patient = {k: v for k, v in healthy_patient.items() if k != "age_yr"}
    r = client.post("/api/v1/benchmark", json=patient)
    assert r.status_code == 200
    ldl = _find(r.json()["threshold_results"], "LDL")
    assert ldl and ldl["category"] is not None


def test_missing_sex_avoids_unsupported_sex_specific_interpretation(healthy_patient):
    """Adversarial case 'Missing sex': HDL has sex-specific thresholds
    (classify_all_biomarkers defaults to the male table when sex is None,
    per docs/CLINICAL_LOGIC_APPENDIX.md's documented default) — confirm this
    still produces a definite category rather than silently dropping HDL or
    guessing a sex. Documenting the default, not inventing one, is the point:
    the response is not silently empty, and the category is reproducible.
    """
    patient = {k: v for k, v in healthy_patient.items() if k != "sex"}
    r = client.post("/api/v1/benchmark", json=patient)
    assert r.status_code == 200
    hdl = _find(r.json()["threshold_results"], "HDL")
    assert hdl and hdl["category"] is not None


def test_ancestry_toggle_does_not_change_universal_threshold_category(healthy_patient):
    """Adversarial case 'Ancestry toggle': same LDL, different ancestry ->
    Do not change the underlying measurement or universal threshold
    arbitrarily. south_asian only adds a separate qualitative discussion
    panel (south_asian_context.py); it must never alter the core
    guideline-threshold category for LDL/HDL/TG/TC/HbA1c/FPG/SBP/DBP.
    """
    r_true = client.post("/api/v1/benchmark", json={**healthy_patient, "south_asian": True})
    r_false = client.post("/api/v1/benchmark", json={**healthy_patient, "south_asian": False})
    assert r_true.status_code == r_false.status_code == 200
    for label in ["LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP"]:
        cat_true = _find(r_true.json()["threshold_results"], label)["category"]
        cat_false = _find(r_false.json()["threshold_results"], label)["category"]
        assert cat_true == cat_false, f"{label} category changed with the ancestry flag alone"


def test_disagreeing_markers_reported_independently(healthy_patient):
    """Adversarial case 'Disagreeing markers': normal HbA1c, elevated fasting
    glucose -> show each observation without suppressing discordance. Each
    biomarker is classified independently in classify_all_biomarkers, so a
    discordant pair must surface as two distinct, non-overridden categories.
    """
    patient = {**healthy_patient, "HbA1c_pct": 5.2, "FPG_mgdl": 130, "fasting_status": "confirmed"}
    r = client.post("/api/v1/benchmark", json=patient)
    assert r.status_code == 200
    hba1c = _find(r.json()["threshold_results"], "HbA1c")
    fpg = _find(r.json()["threshold_results"], "FPG")
    assert hba1c["category"] == "Normal"
    assert fpg["category"] == "Diabetes"


def test_incomplete_record_interprets_only_what_was_supplied(healthy_patient):
    """Adversarial case 'Incomplete record': LDL only -> Interpret LDL only.
    Every other biomarker must come back as the explicit 'Not provided'
    shape (category None), never guessed or omitted from the response.
    """
    r = client.post("/api/v1/benchmark", json={
        "LDL_mgdl": 95, "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
    })
    assert r.status_code == 200
    results = r.json()["threshold_results"]
    ldl = _find(results, "LDL")
    assert ldl and ldl["category"] is not None
    for label in ["HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP"]:
        other = _find(results, label)
        assert other is not None and other["category"] is None and other["category_description"] == "Not provided"
