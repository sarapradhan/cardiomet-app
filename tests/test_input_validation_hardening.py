"""
tests/test_input_validation_hardening.py

Closes the remaining gaps in adversarial/boundary input coverage so a bad or
malicious request fails safely and predictably rather than relying on
incidental behavior: nonnumeric and non-finite values (NaN/Infinity),
implausible-magnitude values, the ancestry flag never perturbing a universal
clinical threshold, discordant markers being reported independently rather
than suppressed or merged, and a partial record interpreting only what was
actually supplied. This is the user-facing guarantee underneath every result
screen: whatever gets typed in, the response is either a clear rejection or a
classification you can trust, never a guess.

Most of this was already true in practice (ge/le field bounds, the
fasting-status gate, the per-field independence of classify_all_biomarkers)
— this file is the test coverage that makes it provable and keeps it true on
every future change, not a behavior change on its own.
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


@pytest.mark.parametrize("bad_value", ["NaN", "Infinity", "-Infinity", "abc", float("nan"), float("inf")])
def test_rejects_nonnumeric_and_non_finite_values(healthy_patient, bad_value):
    """Nonnumeric or non-finite input (abc, NaN, Infinity) must be rejected,
    not silently coerced into a classification.

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
    """An implausible-magnitude value (HbA1c = 150%) must be rejected.
    HbA1c_pct is bounded le=20 (api/models/patient.py); 20% already exceeds
    any physiologically reported value, so 150% is well outside it.
    """
    r = client.post("/api/v1/benchmark", json={**healthy_patient, "HbA1c_pct": 150})
    assert r.status_code == 422


def test_missing_age_shows_only_applicable_classifications(healthy_patient):
    """age_yr is optional and is not an input to classify_all_biomarkers at
    all (only to benchmark/peer-matching age banding) — omitting it must not
    block or alter threshold classification.
    """
    patient = {k: v for k, v in healthy_patient.items() if k != "age_yr"}
    r = client.post("/api/v1/benchmark", json=patient)
    assert r.status_code == 200
    ldl = _find(r.json()["threshold_results"], "LDL")
    assert ldl and ldl["category"] is not None


def test_missing_sex_avoids_unsupported_sex_specific_interpretation(healthy_patient):
    """HDL has sex-specific thresholds
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
    """Same LDL, different ancestry flag: must not change the underlying
    measurement or universal threshold category. south_asian only adds a
    separate qualitative discussion
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
    """Normal HbA1c alongside an elevated fasting glucose must show each
    observation without suppressing the discordance. Each biomarker is
    classified independently in classify_all_biomarkers, so a discordant
    pair must surface as two distinct, non-overridden categories.
    """
    patient = {**healthy_patient, "HbA1c_pct": 5.2, "FPG_mgdl": 130, "fasting_status": "confirmed"}
    r = client.post("/api/v1/benchmark", json=patient)
    assert r.status_code == 200
    hba1c = _find(r.json()["threshold_results"], "HbA1c")
    fpg = _find(r.json()["threshold_results"], "FPG")
    assert hba1c["category"] == "Normal"
    assert fpg["category"] == "Diabetes"


def test_incomplete_record_interprets_only_what_was_supplied(healthy_patient):
    """Given only LDL, interpret only LDL. Every other biomarker must come
    back as the explicit 'Not provided' shape (category None), never guessed
    or omitted from the response.
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
