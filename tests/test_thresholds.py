"""
tests/test_thresholds.py

Boundary tests for sahc_risklens/clinical/thresholds.py and the related
P1 modules (south_asian_context, disclaimers, biomarkers.find_missing_biomarkers).

Every parametrized case corresponds to a row in docs/VALIDATION_PLAN.md
Layer 1.1, and every expected category/range/source is copied from
docs/CLINICAL_LOGIC_APPENDIX.md. These tests call sahc_risklens/clinical/
functions directly \u2014 the API router is not wired in P1 (that is P3), so
this file is independent of tests/test_api_endpoints.py.
"""
from __future__ import annotations

import pytest

from sahc_risklens.clinical.biomarkers import BIOMARKERS, find_missing_biomarkers
from sahc_risklens.clinical.disclaimers import build_physician_guide, get_medication_notes
from sahc_risklens.clinical.south_asian_context import get_south_asian_context
from sahc_risklens.clinical.thresholds import (
    classify_all_biomarkers,
    classify_bmi_south_asian,
    get_all_threshold_categories,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normal_data(**overrides) -> dict:
    """
    Full input with every biomarker at a 'Normal'-ish value (matches
    tests/conftest.py healthy_patient shape). Used as a base so each
    boundary test only needs to override the one biomarker under test.
    """
    data = {
        "LDL_mgdl": 95, "HDL_mgdl": 62, "TG_mgdl": 120, "TC_mgdl": 185,
        "FPG_mgdl": 88, "fasting_status": "confirmed", "HbA1c_pct": 5.2,
        "SBP_mmhg": 115, "DBP_mmhg": 74,
        "BMI_kgm2": 22.1, "age_yr": 45, "sex": "M", "south_asian": True,
        "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
    }
    data.update(overrides)
    return data


def _category_for(label: str, **overrides) -> str | None:
    """Classify with overrides applied, return the category for `label`."""
    results = classify_all_biomarkers(_normal_data(**overrides))
    return next(r["category"] for r in results if r["biomarker"] == label)


# ---------------------------------------------------------------------------
# LDL \u2014 ACC/AHA 2018: <100 Optimal, 100-129 Near Optimal,
#                     130-159 Borderline High, 160-189 High, >=190 Very High
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (99, "Optimal"), (100, "Near Optimal"), (129, "Near Optimal"),
    (130, "Borderline High"), (159, "Borderline High"),
    (160, "High"), (189, "High"), (190, "Very High"),
])
def test_ldl_boundaries(value, expected):
    assert _category_for("LDL", LDL_mgdl=value) == expected


# ---------------------------------------------------------------------------
# HDL \u2014 NCEP ATP III, sex-specific
#   Male:   <40 Low, 40-59 Normal, >=60 Protective
#   Female: <50 Low, 50-59 Normal, >=60 Protective
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (39, "Low"), (40, "Normal"), (59, "Normal"), (60, "Protective"),
])
def test_hdl_male_boundaries(value, expected):
    assert _category_for("HDL", HDL_mgdl=value, sex="M") == expected


@pytest.mark.parametrize("value,expected", [
    (49, "Low"), (50, "Normal"), (59, "Normal"), (60, "Protective"),
])
def test_hdl_female_boundaries(value, expected):
    assert _category_for("HDL", HDL_mgdl=value, sex="F") == expected


def test_hdl_same_value_different_category_by_sex():
    """HDL 48: Low for female (<50) but Normal for male (40-59). Sex-specificity check."""
    assert _category_for("HDL", HDL_mgdl=48, sex="F") == "Low"
    assert _category_for("HDL", HDL_mgdl=48, sex="M") == "Normal"


# ---------------------------------------------------------------------------
# Triglycerides \u2014 ACC/AHA 2018:
#   <150 Normal, 150-199 Borderline High, 200-499 High, >=500 Very High
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (149, "Normal"), (150, "Borderline High"), (199, "Borderline High"),
    (200, "High"), (499, "High"), (500, "Very High"),
])
def test_tg_boundaries(value, expected):
    assert _category_for("TG", TG_mgdl=value) == expected


# ---------------------------------------------------------------------------
# Total Cholesterol \u2014 NCEP ATP III:
#   <200 Desirable, 200-239 Borderline High, >=240 High
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (199, "Desirable"), (200, "Borderline High"), (239, "Borderline High"), (240, "High"),
])
def test_tc_boundaries(value, expected):
    assert _category_for("TC", TC_mgdl=value) == expected


# ---------------------------------------------------------------------------
# HbA1c \u2014 ADA 2024:
#   <5.7 Normal, 5.7-<6.5 Prediabetes, >=6.5 Diabetes
#   (6.49 is the "in-between" case from VALIDATION_PLAN.md \u2014 must be
#   Prediabetes, not Diabetes, confirming the upper bound is exclusive 6.5)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (5.69, "Normal"), (5.7, "Prediabetes"), (6.4, "Prediabetes"),
    (6.49, "Prediabetes"), (6.5, "Diabetes"),
])
def test_hba1c_boundaries(value, expected):
    assert _category_for("HbA1c", HbA1c_pct=value) == expected


# ---------------------------------------------------------------------------
# Fasting Plasma Glucose \u2014 ADA 2024:
#   <100 Normal, 100-125 Prediabetes, >=126 Diabetes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (99, "Normal"), (100, "Prediabetes"), (125, "Prediabetes"), (126, "Diabetes"),
])
def test_fpg_boundaries(value, expected):
    assert _category_for("FPG", FPG_mgdl=value) == expected


# ---------------------------------------------------------------------------
# Fasting Plasma Glucose — fasting-status gating.
# docs/CLINICAL_LOGIC_APPENDIX.md: "Requires PHAFSTHR >= 8. Do not classify
# non-fasting values." Regression coverage for a gap external review found:
# FPG was classified against fasting thresholds regardless of fasting status,
# because there was no fasting_status field at all.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fasting_status", [None, "unknown", "not_fasting"])
def test_fpg_not_classified_without_confirmed_fasting(fasting_status):
    """Default-deny: anything other than an explicit 'confirmed' must not
    produce a fasting-glucose category, even at an unambiguous value."""
    data = _normal_data(FPG_mgdl=140, fasting_status=fasting_status)
    results = classify_all_biomarkers(data)
    fpg = next(r for r in results if r["biomarker"] == "FPG")
    assert fpg["category"] is None
    assert fpg["value"] == 140  # value is still reported, just not categorized
    assert "not classifiable" in fpg["category_description"].lower()
    # Must never render as a diagnostic label for an unconfirmed-fasting draw.
    assert "diabetes" not in fpg["category_description"].lower()


def test_fpg_classified_when_fasting_confirmed():
    data = _normal_data(FPG_mgdl=140, fasting_status="confirmed")
    results = classify_all_biomarkers(data)
    fpg = next(r for r in results if r["biomarker"] == "FPG")
    assert fpg["category"] == "Diabetes"


def test_fpg_missing_fasting_status_field_treated_as_unconfirmed():
    """A caller that never sends fasting_status at all (e.g. an old client
    built before this field existed) must get the safe default, not a silent
    classification."""
    data = _normal_data(FPG_mgdl=140)
    del data["fasting_status"]
    results = classify_all_biomarkers(data)
    fpg = next(r for r in results if r["biomarker"] == "FPG")
    assert fpg["category"] is None


# ---------------------------------------------------------------------------
# Systolic BP \u2014 ACC/AHA 2017:
#   <120 Normal, 120-129 Elevated, 130-139 Stage 1, >=140 Stage 2
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (119, "Normal"), (120, "Elevated"), (129, "Elevated"),
    (130, "Stage 1 Hypertension"), (139, "Stage 1 Hypertension"), (140, "Stage 2 Hypertension"),
])
def test_sbp_boundaries(value, expected):
    assert _category_for("SBP", SBP_mmhg=value) == expected


# ---------------------------------------------------------------------------
# Diastolic BP \u2014 ACC/AHA 2017:
#   <80 Normal, 80-89 Stage 1, >=90 Stage 2
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (79, "Normal"), (80, "Stage 1 Hypertension"), (89, "Stage 1 Hypertension"), (90, "Stage 2 Hypertension"),
])
def test_dbp_boundaries(value, expected):
    assert _category_for("DBP", DBP_mmhg=value) == expected


# ---------------------------------------------------------------------------
# BMI \u2014 Standard WHO (used in threshold_results):
#   <18.5 Underweight, 18.5-24.9 Normal, 25-29.9 Overweight, >=30 Obese
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (18.4, "Underweight"), (18.5, "Normal"), (24.9, "Normal"),
    (25.0, "Overweight"), (29.9, "Overweight"), (30.0, "Obese"),
])
def test_bmi_standard_boundaries(value, expected):
    assert _category_for("BMI", BMI_kgm2=value) == expected


# ---------------------------------------------------------------------------
# BMI \u2014 South Asian context (WHO Expert Consultation 2004):
#   <23 Normal, 23-27.4 Increased risk, >=27.5 High risk
#   Classified separately via classify_bmi_south_asian \u2014 NOT the value in
#   threshold_results, which always uses the standard WHO table above.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    (22.9, "Normal"), (23.0, "Increased risk"), (27.4, "Increased risk"), (27.5, "High risk"),
])
def test_bmi_south_asian_boundaries(value, expected):
    category, _ = classify_bmi_south_asian(value)
    assert category == expected


def test_bmi_245_dual_classification():
    """
    BMI 24.5: Normal by WHO standard (18.5-24.9) but Increased risk by South
    Asian context (>=23). Both must be independently correct \u2014 this is the
    case tests/conftest.py south_asian_bmi_patient is designed to exercise.
    """
    assert _category_for("BMI", BMI_kgm2=24.5) == "Normal"
    sa_category, _ = classify_bmi_south_asian(24.5)
    assert sa_category == "Increased risk"


# ---------------------------------------------------------------------------
# Guideline sources \u2014 must match docs/CLINICAL_LOGIC_APPENDIX.md exactly
# ---------------------------------------------------------------------------

def test_guideline_sources_match_appendix():
    results = classify_all_biomarkers(_normal_data())
    sources = {r["biomarker"]: r["guideline_source"] for r in results}
    assert sources["LDL"] == "ACC/AHA 2018 Cholesterol Guideline"
    assert sources["HDL"] == "NCEP ATP III"
    assert sources["TG"] == "ACC/AHA 2018 Cholesterol Guideline"
    assert sources["TC"] == "NCEP ATP III"
    assert sources["HbA1c"] == "ADA Standards of Medical Care 2024"
    assert sources["FPG"] == "ADA Standards of Medical Care 2024"
    assert sources["SBP"] == "ACC/AHA 2017 High Blood Pressure Guideline"
    assert sources["DBP"] == "ACC/AHA 2017 High Blood Pressure Guideline"
    assert sources["BMI"] == "WHO Global Database on Body Mass Index"


def test_south_asian_bmi_source_matches_appendix():
    items = get_south_asian_context(bmi_value=24.5)
    bmi_item = next(i for i in items if "BMI" in i["factor"])
    assert bmi_item["guideline_source"] == "WHO Expert Consultation on BMI in Asian Populations (2004)"


# ---------------------------------------------------------------------------
# get_all_threshold_categories \u2014 GET /api/v1/thresholds support (P3)
# ---------------------------------------------------------------------------

def test_get_all_threshold_categories_has_required_keys():
    table = get_all_threshold_categories()
    for key in ["LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP",
                "BMI_standard", "BMI_south_asian_context"]:
        assert key in table, f"Missing key: {key}"
        assert len(table[key]) > 0, f"Empty category list for: {key}"


def test_hdl_categories_include_both_sexes():
    table = get_all_threshold_categories()
    category_names = [c["category"] for c in table["HDL"]]
    assert any("Male" in c for c in category_names)
    assert any("Female" in c for c in category_names)


# ---------------------------------------------------------------------------
# Missing biomarkers
# ---------------------------------------------------------------------------

def test_missing_biomarkers_uses_input_field_names():
    """missing_biomarkers must contain input field names (e.g. 'HbA1c_pct'),
    matching BenchmarkResponse.missing_biomarkers (tests/test_api_endpoints.py
    test_missing_hba1c_flagged)."""
    data = _normal_data(HbA1c_pct=None, TG_mgdl=None)
    missing = find_missing_biomarkers(data)
    assert "HbA1c_pct" in missing
    assert "TG_mgdl" in missing
    assert "LDL_mgdl" not in missing


def test_missing_biomarker_classified_as_none_category():
    data = _normal_data(HbA1c_pct=None)
    results = classify_all_biomarkers(data)
    hba1c = next(r for r in results if r["biomarker"] == "HbA1c")
    assert hba1c["category"] is None
    assert hba1c["value"] is None


def test_all_biomarkers_present_when_all_inputs_none():
    """Even with every biomarker None, classify_all_biomarkers must return one
    entry per registered biomarker (no crash, no missing entries)."""
    data = {spec.input_field: None for spec in BIOMARKERS}
    data.update({"sex": None, "south_asian": None, "age_yr": None,
                  "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False})
    results = classify_all_biomarkers(data)
    assert len(results) == len(BIOMARKERS)
    assert all(r["category"] is None for r in results)


# ---------------------------------------------------------------------------
# Medication notes \u2014 do not adjust classifications (Phase 1 rule)
# ---------------------------------------------------------------------------

def test_medication_notes_empty_when_no_flags():
    assert get_medication_notes(_normal_data()) == []


def test_medication_notes_one_per_active_flag():
    data = _normal_data(chol_med=True, bp_med=True)
    notes = get_medication_notes(data)
    assert len(notes) == 2


def test_medication_does_not_change_classification():
    """LDL 162 (High) stays High regardless of chol_med flag \u2014 Phase 1 rule:
    medication status is a separate note, never adjusts the category."""
    without_med = _category_for("LDL", LDL_mgdl=162, chol_med=False)
    with_med = _category_for("LDL", LDL_mgdl=162, chol_med=True)
    assert without_med == with_med == "High"


def test_medication_note_attached_to_affected_biomarker():
    data = _normal_data(LDL_mgdl=162, chol_med=True)
    results = classify_all_biomarkers(data)
    ldl = next(r for r in results if r["biomarker"] == "LDL")
    assert ldl["note"] is not None


# ---------------------------------------------------------------------------
# South Asian context panel
# ---------------------------------------------------------------------------

def test_south_asian_context_always_includes_ascvd_factor():
    items = get_south_asian_context()
    assert len(items) == 1
    assert "ASCVD" in items[0]["factor"] or "Ancestry" in items[0]["factor"]
    assert items[0]["guideline_source"] == "2018 AHA/ACC Cholesterol Guideline"


def test_south_asian_context_bmi_item_only_when_bmi_provided():
    without_bmi = get_south_asian_context()
    with_bmi = get_south_asian_context(bmi_value=24.5)
    assert len(without_bmi) == 1
    assert len(with_bmi) == 2


def test_south_asian_context_does_not_quantify_risk():
    """CLINICAL_LOGIC_APPENDIX.md: 'Do not quantify individual risk.'
    Description text must not contain a numeric risk score pattern like
    a percentage risk figure."""
    items = get_south_asian_context(bmi_value=24.5)
    for item in items:
        assert "%" not in item["description"] or "South Asian" not in item["description"]


# ---------------------------------------------------------------------------
# Physician guide \u2014 template-based, only non-lowest-risk categories
# ---------------------------------------------------------------------------

def test_physician_guide_excludes_normal_results():
    """All-normal patient: physician guide should be empty."""
    results = classify_all_biomarkers(_normal_data())
    guide = build_physician_guide(results)
    assert guide == []


def test_physician_guide_includes_elevated_ldl_only():
    data = _normal_data(LDL_mgdl=162)  # High
    results = classify_all_biomarkers(data)
    guide = build_physician_guide(results)
    biomarkers_in_guide = {g["biomarker"] for g in guide}
    assert "LDL" in biomarkers_in_guide
    assert "HDL" not in biomarkers_in_guide  # HDL is Protective (normal-like) at default 62


def test_physician_guide_prompt_has_no_diagnostic_language():
    """Discussion prompts must not contain diagnostic or prescriptive language."""
    data = _normal_data(LDL_mgdl=162, SBP_mmhg=145)
    results = classify_all_biomarkers(data)
    guide = build_physician_guide(results)
    assert len(guide) >= 2
    for item in guide:
        text = item["discussion_prompt"].lower()
        for phrase in ["you have", "you should take", "this predicts", "diagnos"]:
            assert phrase not in text, f"Prohibited phrase '{phrase}' in: {text}"


def test_physician_guide_cites_guideline_source():
    data = _normal_data(HbA1c_pct=5.9)  # Prediabetes
    results = classify_all_biomarkers(data)
    guide = build_physician_guide(results)
    hba1c_item = next(g for g in guide if g["biomarker"] == "HbA1c")
    assert "ADA Standards of Medical Care 2024" in hba1c_item["guideline_note"]
