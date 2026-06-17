"""tests/test_api_endpoints.py — FastAPI endpoint tests."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def _find(results: list, biomarker: str) -> dict | None:
    return next((r for r in results if r["biomarker"] == biomarker), None)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "nhanes_loaded" in r.json()


def test_required_fields(healthy_patient):
    r = client.post("/api/v1/benchmark", json=healthy_patient)
    assert r.status_code == 200
    for f in ["threshold_results","benchmark_data","south_asian_context","physician_guide",
              "missing_biomarkers","medication_notes","cohort_label","disclaimer","validation_status"]:
        assert f in r.json(), f"Missing: {f}"


def test_disclaimer_non_empty(healthy_patient):
    r = client.post("/api/v1/benchmark", json=healthy_patient)
    assert r.status_code == 200
    d = r.json()["disclaimer"]
    assert isinstance(d, str) and len(d) >= 20


def test_cohort_label_exact(healthy_patient):
    r = client.post("/api/v1/benchmark", json=healthy_patient)
    assert r.json()["cohort_label"] == "NHANES Non-Hispanic Asian"


def test_ldl_162_high(elevated_ldl_patient):
    r = client.post("/api/v1/benchmark", json=elevated_ldl_patient)
    result = _find(r.json()["threshold_results"], "LDL")
    assert result and result["category"] == "High"


def test_hba1c_prediabetes(prediabetes_patient):
    r = client.post("/api/v1/benchmark", json=prediabetes_patient)
    result = _find(r.json()["threshold_results"], "HbA1c")
    assert result and result["category"] == "Prediabetes"


def test_fpg_prediabetes(prediabetes_patient):
    r = client.post("/api/v1/benchmark", json=prediabetes_patient)
    result = _find(r.json()["threshold_results"], "FPG")
    assert result and result["category"] == "Prediabetes"


def test_sbp_stage1_htn(hypertension_patient):
    r = client.post("/api/v1/benchmark", json=hypertension_patient)
    result = _find(r.json()["threshold_results"], "SBP")
    assert result and result["category"] == "Stage 1 Hypertension"


def test_female_hdl_low(female_patient):
    """HDL 48, sex F -> Low (<50 female threshold). Not Normal."""
    r = client.post("/api/v1/benchmark", json=female_patient)
    result = _find(r.json()["threshold_results"], "HDL")
    assert result and result["category"] == "Low"


def test_south_asian_bmi_dual(south_asian_bmi_patient):
    r = client.post("/api/v1/benchmark", json=south_asian_bmi_patient)
    data = r.json()
    bmi = _find(data["threshold_results"], "BMI")
    assert bmi and bmi["category"] == "Normal"
    assert "bmi" in str(data["south_asian_context"]).lower() or "23" in str(data["south_asian_context"])


def test_missing_hba1c_flagged(missing_biomarker_patient):
    r = client.post("/api/v1/benchmark", json=missing_biomarker_patient)
    assert "HbA1c_pct" in r.json()["missing_biomarkers"]


def test_all_none_no_crash():
    r = client.post("/api/v1/benchmark", json={
        "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False})
    assert r.status_code == 200


def test_medication_notes(on_medications_patient):
    r = client.post("/api/v1/benchmark", json=on_medications_patient)
    assert len(r.json()["medication_notes"]) > 0


def test_no_diagnostic_language(elevated_ldl_patient):
    r = client.post("/api/v1/benchmark", json=elevated_ldl_patient)
    text = str(r.json()).lower()
    for phrase in ["you have heart disease","you should take","this predicts your","south asian benchmark"]:
        assert phrase not in text, f"Prohibited phrase: '{phrase}'"


def test_rejects_bad_sex(healthy_patient):
    r = client.post("/api/v1/benchmark", json={**healthy_patient, "sex": "X"})
    assert r.status_code == 422


def test_rejects_negative_ldl(healthy_patient):
    r = client.post("/api/v1/benchmark", json={**healthy_patient, "LDL_mgdl": -5})
    assert r.status_code == 422


def test_thresholds_all_biomarkers():
    r = client.get("/api/v1/thresholds")
    assert r.status_code == 200
    for b in ["LDL","HDL","TG","TC","HbA1c","FPG","SBP","DBP","BMI_standard"]:
        assert b in r.json()
