"""
tests/conftest.py — Shared synthetic patient fixtures.
9 cases per VALIDATION_PLAN.md Layer 2.1. All values match CLINICAL_LOGIC_APPENDIX.md.
"""
from __future__ import annotations

from typing import Any

import pytest


def _base() -> dict[str, Any]:
    return {
        "LDL_mgdl": 95, "HDL_mgdl": 62, "TG_mgdl": 120, "TC_mgdl": 185,
        # fasting_status defaults to "confirmed" here since these fixtures exist
        # to exercise classification, not the fasting-status gate itself — see
        # tests/test_thresholds.py's dedicated fasting-status gating tests.
        "FPG_mgdl": 88, "fasting_status": "confirmed", "HbA1c_pct": 5.2,
        "SBP_mmhg": 115, "DBP_mmhg": 74,
        "BMI_kgm2": 22.1, "age_yr": 45, "sex": "M", "south_asian": True,
        "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
    }


@pytest.fixture
def healthy_patient() -> dict[str, Any]:
    return _base()

@pytest.fixture
def elevated_ldl_patient() -> dict[str, Any]:
    """LDL 162 -> High (160–189, ACC/AHA 2018)"""
    return {**_base(), "LDL_mgdl": 162}

@pytest.fixture
def high_triglycerides_patient() -> dict[str, Any]:
    """TG 245 -> High (200–499, ACC/AHA 2018)"""
    return {**_base(), "TG_mgdl": 245}

@pytest.fixture
def prediabetes_patient() -> dict[str, Any]:
    """HbA1c 5.9 -> Prediabetes (5.7–6.4, ADA 2024). FPG 108 -> Prediabetes (100–125)."""
    return {**_base(), "HbA1c_pct": 5.9, "FPG_mgdl": 108}

@pytest.fixture
def hypertension_patient() -> dict[str, Any]:
    """SBP 138 / DBP 88 -> Stage 1 HTN (130–139 / 80–89, ACC/AHA 2017)"""
    return {**_base(), "SBP_mmhg": 138, "DBP_mmhg": 88}

@pytest.fixture
def on_medications_patient() -> dict[str, Any]:
    """Statin + BP med -> medication notes must appear in output."""
    return {**_base(), "chol_med": True, "bp_med": True}

@pytest.fixture
def missing_biomarker_patient() -> dict[str, Any]:
    """Missing HbA1c and TG -> flagged in missing_biomarkers, no crash."""
    p = _base()
    p["HbA1c_pct"] = None
    p["TG_mgdl"] = None
    return p

@pytest.fixture
def female_patient() -> dict[str, Any]:
    """Female, HDL 48 -> Low by female threshold (<50, NCEP ATP III). Not Normal."""
    return {**_base(), "sex": "F", "HDL_mgdl": 48}

@pytest.fixture
def south_asian_bmi_patient() -> dict[str, Any]:
    """BMI 24.5: Normal (WHO, 18.5–24.9) + Increased risk (South Asian, >=23)."""
    return {**_base(), "BMI_kgm2": 24.5}
