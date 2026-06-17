"""
tests/test_trajectory_api.py

T2 tests — written before implementation (TDD). Covers the stateless
POST /api/v1/trajectory endpoint: contract, validation, safety fields,
multi-draw correctness, and statelessness. See
docs/trajectory/DESIGN_TRAJECTORY_T2_T3.md.
"""
from __future__ import annotations

import datetime as dt

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

_PANEL = {
    "LDL_mgdl": 100, "HDL_mgdl": 55, "TG_mgdl": 120, "TC_mgdl": 180,
    "FPG_mgdl": 95, "HbA1c_pct": 5.4, "SBP_mmhg": 118, "DBP_mmhg": 76,
    "BMI_kgm2": 24.0, "age_yr": 45, "sex": "M", "south_asian": True,
    "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
}


def _draw(date_str: str, **overrides) -> dict:
    return {"draw_date": date_str, "values": {**_PANEL, **overrides}, "label": None}


def _series(*draws: dict) -> dict:
    return {"draws": list(draws)}


def _traj(body: dict, biomarker: str) -> dict:
    return next(t for t in body["trajectories"] if t["biomarker"] == biomarker)


# --------------------------------------------------------------------------
# Contract
# --------------------------------------------------------------------------

def test_endpoint_exists_and_returns_200():
    r = client.post("/api/v1/trajectory", json=_series(
        _draw("2025-12-01", LDL_mgdl=162), _draw("2026-05-01", LDL_mgdl=124)))
    assert r.status_code == 200, r.text


def test_response_has_all_contract_fields():
    r = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01")))
    body = r.json()
    for field in ["trajectories", "interventions", "cohort_label",
                  "disclaimer", "validation_status"]:
        assert field in body, f"missing: {field}"


def test_nine_trajectories_returned():
    r = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01")))
    assert len({t["biomarker"] for t in r.json()["trajectories"]}) == 9


def test_trajectory_point_shape():
    r = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01", LDL_mgdl=165)))
    pt = _traj(r.json(), "LDL")["points"][0]
    for field in ["draw_date", "value", "category", "category_tone"]:
        assert field in pt
    assert pt["category"] == "High"  # 165 -> High, from clinical core


# --------------------------------------------------------------------------
# Safety fields
# --------------------------------------------------------------------------

def test_cohort_label_exact():
    r = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01")))
    assert r.json()["cohort_label"] == "NHANES Non-Hispanic Asian"


def test_disclaimer_present_and_long_enough():
    r = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01")))
    assert len(r.json()["disclaimer"]) >= 20


def test_no_predictive_language_in_response():
    r = client.post("/api/v1/trajectory", json=_series(
        _draw("2025-12-01", LDL_mgdl=162, HbA1c_pct=6.0, chol_med=False),
        _draw("2026-05-01", LDL_mgdl=124, HbA1c_pct=5.5, chol_med=True)))
    text = str(r.json()).lower()
    for phrase in ["will reach", "will develop", "predict", "is working",
                   "% risk", "lowered your", "you should", "we recommend"]:
        assert phrase not in text, f"leaked: {phrase}"


# --------------------------------------------------------------------------
# Multi-draw correctness (through the API)
# --------------------------------------------------------------------------

def test_ldl_improving_over_series():
    r = client.post("/api/v1/trajectory", json=_series(
        _draw("2025-12-01", LDL_mgdl=162), _draw("2026-05-01", LDL_mgdl=124)))
    t = _traj(r.json(), "LDL")
    assert t["direction"] == "improving"
    assert t["change_absolute"] == -38


def test_category_transition_surfaced():
    r = client.post("/api/v1/trajectory", json=_series(
        _draw("2025-12-01", HbA1c_pct=5.9), _draw("2026-05-01", HbA1c_pct=5.4)))
    transitions = _traj(r.json(), "HbA1c")["transitions"]
    assert len(transitions) == 1
    assert transitions[0]["from_category"] == "Prediabetes"
    assert transitions[0]["to_category"] == "Normal"


def test_intervention_surfaced():
    r = client.post("/api/v1/trajectory", json=_series(
        _draw("2025-12-01", LDL_mgdl=162, chol_med=False),
        _draw("2026-05-01", LDL_mgdl=124, chol_med=True)))
    interventions = r.json()["interventions"]
    assert len(interventions) == 1
    assert "cholesterol" in interventions[0]["change"].lower()
    assert "LDL" in interventions[0]["affected_biomarkers"]


def test_draws_unordered_input_still_sorted():
    """Posting newest-first still yields ascending points."""
    r = client.post("/api/v1/trajectory", json=_series(
        _draw("2026-05-01", LDL_mgdl=124), _draw("2025-12-01", LDL_mgdl=162)))
    dates = [p["draw_date"] for p in _traj(r.json(), "LDL")["points"]]
    assert dates == sorted(dates)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def test_empty_series_rejected():
    r = client.post("/api/v1/trajectory", json={"draws": []})
    assert r.status_code == 422


def test_future_date_rejected():
    future = (dt.date.today() + dt.timedelta(days=5)).isoformat()
    r = client.post("/api/v1/trajectory", json=_series(_draw(future)))
    assert r.status_code == 422


def test_bad_biomarker_value_rejected():
    r = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01", sex="X")))
    assert r.status_code == 422


def test_missing_draw_date_rejected():
    r = client.post("/api/v1/trajectory", json={"draws": [{"values": _PANEL}]})
    assert r.status_code == 422


# --------------------------------------------------------------------------
# Statelessness
# --------------------------------------------------------------------------

def test_repeated_calls_identical():
    payload = _series(_draw("2025-12-01", LDL_mgdl=162), _draw("2026-05-01", LDL_mgdl=124))
    a = client.post("/api/v1/trajectory", json=payload).json()
    b = client.post("/api/v1/trajectory", json=payload).json()
    # disclaimer/cohort/validation identical; trajectories identical
    assert a["trajectories"] == b["trajectories"]
    assert a["interventions"] == b["interventions"]


def test_independent_series_do_not_interfere():
    r1 = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01", LDL_mgdl=200)))
    r2 = client.post("/api/v1/trajectory", json=_series(_draw("2026-05-01", LDL_mgdl=80)))
    assert _traj(r1.json(), "LDL")["points"][0]["value"] == 200
    assert _traj(r2.json(), "LDL")["points"][0]["value"] == 80
