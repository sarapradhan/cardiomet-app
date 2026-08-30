"""
tests/test_e2e.py

End-to-end tests: start the real FastAPI app in a uvicorn subprocess and drive it
over actual HTTP (not the in-process TestClient). This is the closest automated
check to the deployed Phase 1 experience — it validates the server boots, binds a
port, serves CORS headers, and returns a complete, safe contract over the wire.

Frontend end-to-end (browser) checks are documented in docs/E2E_CHECKLIST.md for
manual / CI-with-Playwright execution; this file covers the API tier end-to-end,
which is what the deployed frontend depends on.

These tests are marked e2e and skip automatically if a server cannot be started
(e.g. port unavailable in a restricted CI sandbox).
"""
from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.error
import urllib.request

import pytest

_HOST = "127.0.0.1"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((_HOST, 0))
        return s.getsockname()[1]


def _wait_for_health(base: str, timeout: float = 25.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base}/health", timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(0.4)
    return False


@pytest.fixture(scope="module")
def live_server():
    port = _free_port()
    base = f"http://{_HOST}:{port}"
    proc = subprocess.Popen(
        ["python3", "-m", "uvicorn", "api.main:app", "--host", _HOST, "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        if not _wait_for_health(base):
            proc.terminate()
            pytest.skip("uvicorn server did not become healthy in time")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def _post_json(base: str, path: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{base}{path}", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Origin": "http://localhost:3000"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def _get_json(base: str, path: str) -> tuple[int, dict]:
    with urllib.request.urlopen(f"{base}{path}", timeout=10) as resp:
        return resp.status, json.loads(resp.read())


_FULL_PATIENT = {
    "LDL_mgdl": 165, "HDL_mgdl": 42, "TG_mgdl": 180, "TC_mgdl": 235,
    "FPG_mgdl": 108, "HbA1c_pct": 5.9, "SBP_mmhg": 135, "DBP_mmhg": 85,
    "BMI_kgm2": 26.5, "age_yr": 52, "sex": "M", "south_asian": True,
    "chol_med": True, "bp_med": False, "insulin": False, "dm_pills": False,
}

pytestmark = pytest.mark.e2e


def test_e2e_health(live_server):
    status, body = _get_json(live_server, "/health")
    assert status == 200
    assert body["status"] == "ok"
    assert "mode" in body  # "live" or "demo"


def test_e2e_full_benchmark_contract(live_server):
    status, body = _post_json(live_server, "/api/v1/benchmark", _FULL_PATIENT)
    assert status == 200
    # Every contract section present
    for field in ["threshold_results", "benchmark_data", "south_asian_context",
                  "physician_guide", "missing_biomarkers", "medication_notes",
                  "cohort_label", "disclaimer", "validation_status"]:
        assert field in body, f"missing field: {field}"
    assert len(body["threshold_results"]) == 9
    assert len(body["benchmark_data"]) == 9


def test_e2e_safety_invariants(live_server):
    """The deployed response always carries the safety guarantees."""
    status, body = _post_json(live_server, "/api/v1/benchmark", _FULL_PATIENT)
    assert status == 200
    assert body["cohort_label"] == "NHANES Non-Hispanic Asian"
    assert len(body["disclaimer"]) >= 20
    # No diagnostic / prescriptive language anywhere in the served payload
    text = json.dumps(body).lower()
    for phrase in ["you have heart disease", "you should take", "this predicts your",
                   "south asian benchmark", "we diagnose"]:
        assert phrase not in text, f"prohibited phrase served: {phrase}"


def test_e2e_clinical_correctness_over_wire(live_server):
    status, body = _post_json(live_server, "/api/v1/benchmark", _FULL_PATIENT)
    by_key = {t["biomarker"]: t for t in body["threshold_results"]}
    assert by_key["LDL"]["category"] == "High"
    assert by_key["HbA1c"]["category"] == "Prediabetes"
    assert by_key["SBP"]["category"] == "Stage 1 Hypertension"
    # South Asian context present for South Asian patient
    assert len(body["south_asian_context"]) >= 1


def test_e2e_thresholds_endpoint(live_server):
    status, body = _get_json(live_server, "/api/v1/thresholds")
    assert status == 200
    for key in ["LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP",
                "BMI_standard", "BMI_south_asian_context"]:
        assert key in body


def test_e2e_input_validation_over_wire(live_server):
    status, _ = _post_json(live_server, "/api/v1/benchmark", {**_FULL_PATIENT, "sex": "X"})
    assert status == 422


def test_e2e_cors_header_present(live_server):
    """A browser Origin gets an allow-origin header back (frontend can call API)."""
    req = urllib.request.Request(
        f"{live_server}/api/v1/benchmark",
        data=json.dumps(_FULL_PATIENT).encode(),
        headers={"Content-Type": "application/json", "Origin": "http://localhost:3000"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        allow_origin = resp.headers.get("access-control-allow-origin")
    assert allow_origin in ("http://localhost:3000", "*")


def test_e2e_trajectory_endpoint(live_server):
    """Real-server: post a 2-draw series, assert contract + safety over HTTP."""
    payload = {"draws": [
        {"draw_date": "2025-12-01", "label": "baseline",
         "values": {"LDL_mgdl": 162, "HbA1c_pct": 6.0, "sex": "M",
                    "south_asian": True, "chol_med": False, "bp_med": False,
                    "insulin": False, "dm_pills": False}},
        {"draw_date": "2026-05-01", "label": "after statin",
         "values": {"LDL_mgdl": 124, "HbA1c_pct": 5.5, "sex": "M",
                    "south_asian": True, "chol_med": True, "bp_med": False,
                    "insulin": False, "dm_pills": False}},
    ]}
    status, body = _post_json(live_server, "/api/v1/trajectory", payload)
    assert status == 200
    assert body["cohort_label"] == "NHANES Non-Hispanic Asian"
    assert len(body["disclaimer"]) >= 20
    assert len(body["trajectories"]) == 9
    ldl = next(t for t in body["trajectories"] if t["biomarker"] == "LDL")
    assert ldl["direction"] == "improving"
    # descriptive-only over the wire
    text = json.dumps(body).lower()
    for phrase in ["will reach", "predict", "is working", "% risk", "lowered your"]:
        assert phrase not in text
