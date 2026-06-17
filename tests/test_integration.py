"""
tests/test_integration.py

Integration tests: exercise the full request pipeline through the FastAPI app
(BiomarkerInput -> clinical + benchmark + context + guide -> BenchmarkResponse)
and assert that the components agree with each other. Where test_thresholds.py
checks one function and test_api_endpoints.py checks one field, these tests check
that the pieces stay consistent end-to-end for realistic patients.

Uses the 9 synthetic fixtures from conftest.py so the scenarios match
VALIDATION_PLAN.md Layer 2.1.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _post(patient: dict) -> dict:
    r = client.post("/api/v1/benchmark", json=patient)
    assert r.status_code == 200, r.text
    return r.json()


def _result_for(body: dict, biomarker: str) -> dict | None:
    return next((t for t in body["threshold_results"] if t["biomarker"] == biomarker), None)


def _benchmark_for(body: dict, biomarker: str) -> dict | None:
    return next((b for b in body["benchmark_data"] if b["biomarker"] == biomarker), None)


# ---------------------------------------------------------------------------
# Pipeline shape — every section is internally consistent
# ---------------------------------------------------------------------------

def test_threshold_and_benchmark_biomarkers_align(healthy_patient):
    """Every benchmarked biomarker also has a threshold result, and vice versa."""
    body = _post(healthy_patient)
    threshold_keys = {t["biomarker"] for t in body["threshold_results"]}
    benchmark_keys = {b["biomarker"] for b in body["benchmark_data"]}
    assert threshold_keys == benchmark_keys


def test_patient_values_match_across_sections(elevated_ldl_patient):
    """The LDL value reported in threshold_results equals the one in benchmark_data."""
    body = _post(elevated_ldl_patient)
    t = _result_for(body, "LDL")
    b = _benchmark_for(body, "LDL")
    assert t["value"] == b["patient_value"] == 162


def test_physician_guide_subset_of_threshold_results(hypertension_patient):
    """Every physician-guide item corresponds to a real, non-normal threshold result."""
    body = _post(hypertension_patient)
    guide_keys = {(g["biomarker"], g["category"]) for g in body["physician_guide"]}
    threshold_keys = {(t["biomarker"], t["category"]) for t in body["threshold_results"]}
    assert guide_keys.issubset(threshold_keys)


def test_normal_categories_excluded_from_guide(healthy_patient):
    """An all-normal patient produces an empty physician guide."""
    body = _post(healthy_patient)
    assert body["physician_guide"] == []


# ---------------------------------------------------------------------------
# Clinical scenario correctness through the full stack
# ---------------------------------------------------------------------------

def test_prediabetes_scenario(prediabetes_patient):
    body = _post(prediabetes_patient)
    assert _result_for(body, "HbA1c")["category"] == "Prediabetes"
    assert _result_for(body, "FPG")["category"] == "Prediabetes"
    guide_biomarkers = {g["biomarker"] for g in body["physician_guide"]}
    assert {"HbA1c", "FPG"}.issubset(guide_biomarkers)


def test_hypertension_scenario(hypertension_patient):
    body = _post(hypertension_patient)
    assert _result_for(body, "SBP")["category"] == "Stage 1 Hypertension"
    assert _result_for(body, "DBP")["category"] == "Stage 1 Hypertension"


def test_female_hdl_scenario(female_patient):
    """Sex flows through to HDL classification: 48 mg/dL is Low for a female."""
    body = _post(female_patient)
    assert _result_for(body, "HDL")["category"] == "Low"


def test_medication_scenario(on_medications_patient):
    """Medication notes appear and affected biomarkers carry a note, but the
    classification is unchanged versus the same values without medication."""
    body = _post(on_medications_patient)
    assert len(body["medication_notes"]) == 2  # chol_med + bp_med
    ldl = _result_for(body, "LDL")
    assert ldl["note"] is not None  # chol_med affects LDL

    # Same values, no meds -> same category, no note
    no_med = {**on_medications_patient, "chol_med": False, "bp_med": False}
    body2 = _post(no_med)
    assert _result_for(body2, "LDL")["category"] == ldl["category"]
    assert _result_for(body2, "LDL")["note"] is None
    assert body2["medication_notes"] == []


def test_south_asian_bmi_dual_view(south_asian_bmi_patient):
    """BMI 24.5 is 'Normal' (standard WHO) in threshold_results, and the South
    Asian context panel separately flags 'Increased risk' — never conflated."""
    body = _post(south_asian_bmi_patient)
    assert _result_for(body, "BMI")["category"] == "Normal"
    sa_text = " ".join(item["description"] for item in body["south_asian_context"])
    assert "Increased risk" in sa_text


def test_missing_biomarker_scenario(missing_biomarker_patient):
    """Missing HbA1c/TG are flagged, still appear as threshold cards with null
    category, and do not crash benchmark generation."""
    body = _post(missing_biomarker_patient)
    assert "HbA1c_pct" in body["missing_biomarkers"]
    assert "TG_mgdl" in body["missing_biomarkers"]
    assert _result_for(body, "HbA1c")["category"] is None
    # benchmark distribution still present for the missing biomarker
    assert _benchmark_for(body, "HbA1c")["cohort_median"] > 0
    assert _benchmark_for(body, "HbA1c")["patient_value"] is None


# ---------------------------------------------------------------------------
# South Asian context gating
# ---------------------------------------------------------------------------

def test_south_asian_context_present_when_flagged(healthy_patient):
    body = _post(healthy_patient)  # south_asian True in fixture
    assert len(body["south_asian_context"]) >= 1


def test_south_asian_context_absent_when_not_flagged(healthy_patient):
    body = _post({**healthy_patient, "south_asian": False})
    assert body["south_asian_context"] == []


# ---------------------------------------------------------------------------
# Benchmark integration with real/demo cohort
# ---------------------------------------------------------------------------

def test_benchmark_uses_nhanes_cohort_label(healthy_patient):
    body = _post(healthy_patient)
    assert body["cohort_label"] == "NHANES Non-Hispanic Asian"
    for b in body["benchmark_data"]:
        assert b["cohort_label"] == "NHANES Non-Hispanic Asian"
        assert b["cohort_n"] > 0


def test_thresholds_endpoint_matches_classification_sources(elevated_ldl_patient):
    """guideline_source for LDL in /benchmark matches the LDL source in /thresholds."""
    body = _post(elevated_ldl_patient)
    ldl_source = _result_for(body, "LDL")["guideline_source"]
    thresholds = client.get("/api/v1/thresholds").json()
    assert thresholds["LDL"][0]["guideline_source"] == ldl_source
