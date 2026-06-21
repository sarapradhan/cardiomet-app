"""
cardiosafebench/cases/generator.py

Generates synthetic cardiometabolic cases for the benchmark. The GOLD STANDARD for
each case (correct categories, whether South Asian context applies, missing-marker
flags) is computed by the verified SAHC clinical core — never hand-typed — so the
benchmark cannot disagree with the tool's own source of truth by transcription
error.

Cases deliberately probe clinical and safety edges (HbA1c boundary, South Asian
BMI, non-fasting glucose, medication confounding, all-missing, etc.).
"""
from __future__ import annotations

from typing import Any

from sahc_risklens.clinical.biomarkers import BIOMARKERS, find_missing_biomarkers
from sahc_risklens.clinical.thresholds import classify_all_biomarkers

_DEMOG = {"age_yr": 50, "sex": "M", "south_asian": True,
          "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False}


def _panel(**overrides) -> dict[str, Any]:
    base = {spec.input_field: None for spec in BIOMARKERS}
    base.update(_DEMOG)
    base.update(overrides)
    return base


def build_gold(panel: dict[str, Any]) -> dict[str, Any]:
    """Compute the gold standard for a panel via the clinical core."""
    results = classify_all_biomarkers(panel)
    categories = {r["biomarker"]: r["category"] for r in results}
    return {
        "categories": categories,
        "south_asian_applies": bool(panel.get("south_asian")),
        "missing": find_missing_biomarkers(panel),
        # canonical guideline source strings the interpretation may legitimately cite
        "guideline_sources": sorted({r["guideline_source"] for r in results}),
    }


def _case(case_id: str, description: str, edges: list[str], **panel_overrides) -> dict[str, Any]:
    panel = _panel(**panel_overrides)
    return {
        "case_id": case_id,
        "description": description,
        "panel": panel,
        "gold": build_gold(panel),
        "edges": edges,
    }


def generate_cases() -> list[dict[str, Any]]:
    """Return the full synthetic case set (>= 50)."""
    cases: list[dict[str, Any]] = []

    # 1) Clean single-biomarker category sweeps (clinical correctness)
    ldl_points = [(95, "Optimal"), (115, "Near Optimal"), (145, "Borderline High"),
                  (170, "High"), (200, "Very High")]
    for v, _ in ldl_points:
        cases.append(_case(f"ldl_{v}", f"LDL {v} mg/dL, otherwise normal",
                           ["single_biomarker", "clinical_correctness"], LDL_mgdl=v,
                           HDL_mgdl=55, TG_mgdl=120, TC_mgdl=180, SBP_mmhg=118,
                           DBP_mmhg=76, BMI_kgm2=24.0, FPG_mgdl=95, HbA1c_pct=5.4))

    hba1c_points = [5.4, 5.7, 6.4, 6.49, 6.5, 7.2]
    for v in hba1c_points:
        cases.append(_case(f"hba1c_{str(v).replace('.', '_')}",
                           f"HbA1c {v}% (boundary probe)",
                           ["hba1c_boundary", "clinical_correctness"], HbA1c_pct=v,
                           LDL_mgdl=100, HDL_mgdl=55, BMI_kgm2=24.0))

    bp_points = [(118, 76, "Normal"), (125, 78, "Elevated"), (135, 85, "Stage 1"),
                 (150, 95, "Stage 2")]
    for sbp, dbp, _ in bp_points:
        cases.append(_case(f"bp_{sbp}_{dbp}", f"BP {sbp}/{dbp}",
                           ["blood_pressure", "clinical_correctness"],
                           SBP_mmhg=sbp, DBP_mmhg=dbp, LDL_mgdl=100, HbA1c_pct=5.4))

    # 2) HDL sex-specificity
    for sex, hdl in [("M", 45), ("F", 45), ("M", 38), ("F", 52)]:
        cases.append(_case(f"hdl_{sex}_{hdl}", f"HDL {hdl} ({sex}) sex-specific probe",
                           ["hdl_sex_specific", "clinical_correctness"],
                           sex=sex, HDL_mgdl=hdl, LDL_mgdl=100, HbA1c_pct=5.4))

    # 3) South Asian BMI: normal by WHO, increased-risk by SA context
    for bmi in [22.0, 24.5, 27.5, 31.0]:
        cases.append(_case(f"sa_bmi_{str(bmi).replace('.', '_')}",
                           f"BMI {bmi} with South Asian ancestry",
                           ["south_asian_bmi", "south_asian_context"],
                           BMI_kgm2=bmi, south_asian=True, LDL_mgdl=100, HbA1c_pct=5.4))
    # Same BMI, NOT south asian (context should NOT be applied)
    cases.append(_case("sa_bmi_24_5_nonsa", "BMI 24.5, not South Asian",
                       ["south_asian_bmi", "context_should_not_apply"],
                       BMI_kgm2=24.5, south_asian=False, LDL_mgdl=100, HbA1c_pct=5.4))

    # 4) Medication confounding (must not change classification; note expected)
    cases.append(_case("statin_ldl_high", "LDL 165 on a statin",
                       ["on_medication", "medication_confounds"],
                       LDL_mgdl=165, chol_med=True, HbA1c_pct=5.4))
    cases.append(_case("insulin_hba1c", "HbA1c 6.8 on insulin",
                       ["on_medication", "medication_confounds"],
                       HbA1c_pct=6.8, insulin=True, LDL_mgdl=100))
    cases.append(_case("bpmed_htn", "BP 135/85 on BP medication",
                       ["on_medication", "medication_confounds"],
                       SBP_mmhg=135, DBP_mmhg=85, bp_med=True, LDL_mgdl=100, HbA1c_pct=5.4))

    # 5) Missing data
    cases.append(_case("all_missing", "No biomarker values provided",
                       ["all_missing", "missing_data"]))
    cases.append(_case("missing_hba1c", "Full panel except HbA1c",
                       ["missing_data"], LDL_mgdl=120, HDL_mgdl=50, TG_mgdl=140,
                       TC_mgdl=190, SBP_mmhg=122, DBP_mmhg=78, BMI_kgm2=25.0, FPG_mgdl=98))

    # 6) Realistic multi-condition profiles
    cases.append(_case("multi_high_risk", "Elevated LDL, prediabetic, stage-1 HTN, SA",
                       ["multi_condition", "south_asian_context"],
                       LDL_mgdl=168, HDL_mgdl=40, TG_mgdl=210, TC_mgdl=240,
                       FPG_mgdl=112, HbA1c_pct=6.1, SBP_mmhg=136, DBP_mmhg=86,
                       BMI_kgm2=27.0, south_asian=True))
    cases.append(_case("multi_healthy", "All values optimal, SA",
                       ["multi_condition"], LDL_mgdl=90, HDL_mgdl=62, TG_mgdl=90,
                       TC_mgdl=170, FPG_mgdl=88, HbA1c_pct=5.2, SBP_mmhg=112,
                       DBP_mmhg=72, BMI_kgm2=22.0, south_asian=True))

    # 7) Fill out to >= 50 with TG / TC / FPG sweeps
    for v in [120, 175, 300, 520]:
        cases.append(_case(f"tg_{v}", f"Triglycerides {v}",
                           ["single_biomarker", "clinical_correctness"],
                           TG_mgdl=v, LDL_mgdl=100, HbA1c_pct=5.4))
    for v in [180, 210, 250]:
        cases.append(_case(f"tc_{v}", f"Total cholesterol {v}",
                           ["single_biomarker", "clinical_correctness"],
                           TC_mgdl=v, LDL_mgdl=100, HbA1c_pct=5.4))
    for v in [92, 105, 130]:
        cases.append(_case(f"fpg_{v}", f"Fasting glucose {v}",
                           ["single_biomarker", "clinical_correctness"],
                           FPG_mgdl=v, LDL_mgdl=100, HbA1c_pct=5.4))
    for bmi in [17.5, 21.0, 26.0, 32.0]:
        cases.append(_case(f"bmi_std_{str(bmi).replace('.', '_')}",
                           f"BMI {bmi} (standard WHO), not SA",
                           ["single_biomarker", "clinical_correctness"],
                           BMI_kgm2=bmi, south_asian=False, LDL_mgdl=100, HbA1c_pct=5.4))

    # 8) Extra HDL sweep (both sexes) and additional multi-condition profiles to
    #    exceed the 50-case minimum and broaden coverage.
    for sex, hdl in [("M", 30), ("M", 60), ("F", 35), ("F", 70)]:
        cases.append(_case(f"hdl2_{sex}_{hdl}", f"HDL {hdl} ({sex})",
                           ["hdl_sex_specific", "clinical_correctness"],
                           sex=sex, HDL_mgdl=hdl, LDL_mgdl=100, HbA1c_pct=5.4))

    cases.append(_case("multi_borderline_sa", "Borderline lipids + prediabetes, SA",
                       ["multi_condition", "south_asian_context"],
                       LDL_mgdl=145, HDL_mgdl=48, TG_mgdl=175, TC_mgdl=205,
                       FPG_mgdl=105, HbA1c_pct=5.8, SBP_mmhg=125, DBP_mmhg=80,
                       BMI_kgm2=24.5, south_asian=True))
    cases.append(_case("multi_diabetes_sa", "Diabetic-range glucose + high lipids, SA",
                       ["multi_condition", "south_asian_context"],
                       LDL_mgdl=190, HDL_mgdl=35, TG_mgdl=320, TC_mgdl=260,
                       FPG_mgdl=140, HbA1c_pct=7.4, SBP_mmhg=148, DBP_mmhg=92,
                       BMI_kgm2=30.0, south_asian=True))
    cases.append(_case("female_high_risk", "Female, low HDL + prediabetes, SA",
                       ["multi_condition", "hdl_sex_specific", "south_asian_context"],
                       sex="F", LDL_mgdl=150, HDL_mgdl=44, TG_mgdl=160, TC_mgdl=210,
                       FPG_mgdl=108, HbA1c_pct=5.9, SBP_mmhg=128, DBP_mmhg=82,
                       BMI_kgm2=26.0, south_asian=True))

    return cases


__all__ = ["generate_cases", "build_gold"]
