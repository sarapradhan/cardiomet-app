"""
tests/test_smoke.py

Smoke tests: confirm every component imports cleanly and its primary entry point
runs without raising on a minimal happy-path input. These are deliberately
shallow and fast — they catch import errors, signature drift, and gross wiring
breaks before the deeper correctness suites run. One test per component.
"""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

_MINIMAL_PATIENT = {
    "LDL_mgdl": 100, "HDL_mgdl": 55, "TG_mgdl": 120, "TC_mgdl": 180,
    "FPG_mgdl": 95, "HbA1c_pct": 5.4, "SBP_mmhg": 118, "DBP_mmhg": 76,
    "BMI_kgm2": 24.0, "age_yr": 45, "sex": "M", "south_asian": True,
    "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
}


# ---------------------------------------------------------------------------
# Imports — every module in the package loads
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module", [
    "sahc_risklens.config",
    "sahc_risklens.clinical.biomarkers",
    "sahc_risklens.clinical.thresholds",
    "sahc_risklens.clinical.south_asian_context",
    "sahc_risklens.clinical.disclaimers",
    "sahc_risklens.data.nhanes_loader",
    "sahc_risklens.data.cohort_filters",
    "sahc_risklens.data.missingness",
    "sahc_risklens.data.demo_cohort",
    "sahc_risklens.benchmark.percentile",
    "sahc_risklens.trajectory.series",
    "sahc_risklens.trajectory.health_file",
    "sahc_risklens.trajectory.analytics",
    "api.main",
    "api.models.patient",
    "api.models.results",
    "api.routers.benchmark",
    "api.routers.thresholds",
    "api.routers.health",
])
def test_module_imports(module):
    assert importlib.import_module(module) is not None


# ---------------------------------------------------------------------------
# Component entry points — each runs on minimal input
# ---------------------------------------------------------------------------

def test_smoke_classify_all_biomarkers():
    from sahc_risklens.clinical.thresholds import classify_all_biomarkers
    results = classify_all_biomarkers(_MINIMAL_PATIENT)
    assert len(results) == 9
    assert all("biomarker" in r and "category" in r for r in results)


def test_smoke_get_all_threshold_categories():
    from sahc_risklens.clinical.thresholds import get_all_threshold_categories
    table = get_all_threshold_categories()
    assert "LDL" in table and "BMI_south_asian_context" in table


def test_smoke_classify_bmi_south_asian():
    from sahc_risklens.clinical.thresholds import classify_bmi_south_asian
    category, desc = classify_bmi_south_asian(24.5)
    assert category == "Increased risk"


def test_smoke_find_missing_biomarkers():
    from sahc_risklens.clinical.biomarkers import find_missing_biomarkers
    assert find_missing_biomarkers(_MINIMAL_PATIENT) == []


def test_smoke_get_south_asian_context():
    from sahc_risklens.clinical.south_asian_context import get_south_asian_context
    items = get_south_asian_context(bmi_value=24.5)
    assert len(items) == 2


def test_smoke_build_physician_guide():
    from sahc_risklens.clinical.disclaimers import build_physician_guide
    from sahc_risklens.clinical.thresholds import classify_all_biomarkers
    guide = build_physician_guide(classify_all_biomarkers({**_MINIMAL_PATIENT, "LDL_mgdl": 165}))
    assert any(g["biomarker"] == "LDL" for g in guide)


def test_smoke_get_medication_notes():
    from sahc_risklens.clinical.disclaimers import get_medication_notes
    assert get_medication_notes({**_MINIMAL_PATIENT, "chol_med": True})


def test_smoke_get_benchmark_data():
    from sahc_risklens.benchmark.percentile import get_benchmark_data
    points = get_benchmark_data(_MINIMAL_PATIENT)
    assert len(points) == 9
    assert all(p["cohort_label"] == "NHANES Non-Hispanic Asian" for p in points)


def test_smoke_get_cohort_percentiles():
    from sahc_risklens.benchmark.percentile import get_cohort_percentiles
    table = get_cohort_percentiles()
    assert len(table) == 9


def test_smoke_cohort_filter():
    import pandas as pd

    from sahc_risklens.data.cohort_filters import filter_non_hispanic_asian
    df = pd.DataFrame({"SEQN": [1, 2], "RIDRETH3": [6, 3]})
    assert len(filter_non_hispanic_asian(df)) == 1


def test_smoke_missingness_report():
    import pandas as pd

    from sahc_risklens.data.missingness import missingness_report
    rep = missingness_report(pd.DataFrame({"A": [1, None]}))
    assert rep["A"]["n_missing"] == 1


def test_smoke_demo_cohort():
    from sahc_risklens.data.demo_cohort import get_demo_percentiles
    assert len(get_demo_percentiles()) == 9


# ---------------------------------------------------------------------------
# API endpoints — each route answers
# ---------------------------------------------------------------------------

def test_smoke_health_endpoint():
    assert client.get("/health").status_code == 200


def test_smoke_benchmark_endpoint():
    assert client.post("/api/v1/benchmark", json=_MINIMAL_PATIENT).status_code == 200


def test_smoke_thresholds_endpoint():
    assert client.get("/api/v1/thresholds").status_code == 200


def test_smoke_openapi_schema():
    """The app boots far enough to produce its OpenAPI schema."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "/api/v1/benchmark" in r.json()["paths"]


def test_smoke_make_series_and_analyze():
    import datetime as dt

    from sahc_risklens.trajectory.analytics import analyze_series
    from sahc_risklens.trajectory.series import BiomarkerDraw, make_series
    series = make_series([
        BiomarkerDraw(dt.date(2025, 12, 1), {"LDL_mgdl": 162}),
        BiomarkerDraw(dt.date(2026, 5, 1), {"LDL_mgdl": 124}),
    ])
    a = analyze_series(series)
    assert len(a.trajectories) == 9


def test_smoke_health_file_round_trip():
    import datetime as dt

    from sahc_risklens.trajectory.health_file import from_health_file, to_health_file
    from sahc_risklens.trajectory.series import BiomarkerDraw, make_series
    s = make_series([BiomarkerDraw(dt.date(2026, 1, 1), {"LDL_mgdl": 100})])
    assert from_health_file(to_health_file(s)).draws[0].values["LDL_mgdl"] == 100


def test_smoke_static_mount_does_not_shadow_api():
    """The frontend static mount must not shadow /health or /api routes.

    Checked by reachability (robust across FastAPI/Starlette versions) rather
    than by introspecting route internals.
    """
    from fastapi.testclient import TestClient
    client = TestClient(app)
    # /health responds (not swallowed by the static mount)
    assert client.get("/health").status_code == 200
    # API endpoints respond to a minimal valid request
    r = client.post("/api/v1/benchmark", json={
        "sex": "M", "south_asian": False, "chol_med": False, "bp_med": False,
        "insulin": False, "dm_pills": False,
    })
    assert r.status_code == 200
    r2 = client.post("/api/v1/trajectory", json={"draws": [
        {"draw_date": "2026-01-01", "label": None, "values": {
            "sex": "M", "south_asian": False, "chol_med": False, "bp_med": False,
            "insulin": False, "dm_pills": False}},
    ]})
    assert r2.status_code == 200
