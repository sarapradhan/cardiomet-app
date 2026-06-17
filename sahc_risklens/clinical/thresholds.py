"""
sahc_risklens/clinical/thresholds.py

Clinical threshold classification.

SOURCE OF TRUTH: docs/CLINICAL_LOGIC_APPENDIX.md
Every (lower_bound, category, range_description, guideline_source) tuple below
is copied verbatim from that document. Do not edit values here without updating
docs/CLINICAL_LOGIC_APPENDIX.md in the same change (see .project/skills/update_docs.md).

Classification algorithm:
Each table is an ascending list of (lower_bound_inclusive, category, range_description).
For a given value, the matching category is the LAST entry whose lower_bound <= value.
This means upper bounds are implicit (the next entry's lower_bound) — e.g. for LDL,
"Near Optimal" (lower_bound=100) implicitly extends up to (but not including) 130,
where "Borderline High" begins. range_description strings are independent display
text matching the appendix's printed ranges and are not used for classification math.
"""
from __future__ import annotations

from sahc_risklens.clinical.biomarkers import BIOMARKERS, get_field, find_missing_biomarkers

Table = list[tuple[float, str, str]]

# ---------------------------------------------------------------------------
# Threshold tables — docs/CLINICAL_LOGIC_APPENDIX.md
# ---------------------------------------------------------------------------

_LDL_SOURCE = "ACC/AHA 2018 Cholesterol Guideline"
_LDL_TABLE: Table = [
    (float("-inf"), "Optimal",         "< 100 mg/dL"),
    (100,           "Near Optimal",    "100-129 mg/dL"),
    (130,           "Borderline High", "130-159 mg/dL"),
    (160,           "High",            "160-189 mg/dL"),
    (190,           "Very High",       ">= 190 mg/dL"),
]

_HDL_SOURCE = "NCEP ATP III"
_HDL_MALE_TABLE: Table = [
    (float("-inf"), "Low",        "< 40 mg/dL"),
    (40,            "Normal",     "40-59 mg/dL"),
    (60,            "Protective", ">= 60 mg/dL"),
]
_HDL_FEMALE_TABLE: Table = [
    (float("-inf"), "Low",        "< 50 mg/dL"),
    (50,            "Normal",     "50-59 mg/dL"),
    (60,            "Protective", ">= 60 mg/dL"),
]

_TG_SOURCE = "ACC/AHA 2018 Cholesterol Guideline"
_TG_TABLE: Table = [
    (float("-inf"), "Normal",          "< 150 mg/dL"),
    (150,           "Borderline High", "150-199 mg/dL"),
    (200,           "High",            "200-499 mg/dL"),
    (500,           "Very High",       ">= 500 mg/dL"),
]

_TC_SOURCE = "NCEP ATP III"
_TC_TABLE: Table = [
    (float("-inf"), "Desirable",       "< 200 mg/dL"),
    (200,           "Borderline High", "200-239 mg/dL"),
    (240,           "High",            ">= 240 mg/dL"),
]

_HBA1C_SOURCE = "ADA Standards of Medical Care 2024"
_HBA1C_TABLE: Table = [
    (float("-inf"), "Normal",      "< 5.7%"),
    (5.7,           "Prediabetes", "5.7-6.4%"),
    (6.5,           "Diabetes",    ">= 6.5%"),
]

_FPG_SOURCE = "ADA Standards of Medical Care 2024"
_FPG_TABLE: Table = [
    (float("-inf"), "Normal",      "< 100 mg/dL"),
    (100,           "Prediabetes", "100-125 mg/dL"),
    (126,           "Diabetes",    ">= 126 mg/dL"),
]

_BP_SOURCE = "ACC/AHA 2017 High Blood Pressure Guideline"
_SBP_TABLE: Table = [
    (float("-inf"), "Normal",               "< 120 mm Hg"),
    (120,           "Elevated",             "120-129 mm Hg"),
    (130,           "Stage 1 Hypertension", "130-139 mm Hg"),
    (140,           "Stage 2 Hypertension", ">= 140 mm Hg"),
]
_DBP_TABLE: Table = [
    (float("-inf"), "Normal",               "< 80 mm Hg"),
    (80,            "Stage 1 Hypertension", "80-89 mm Hg"),
    (90,            "Stage 2 Hypertension", ">= 90 mm Hg"),
]

_BMI_STANDARD_SOURCE = "WHO Global Database on Body Mass Index"
_BMI_STANDARD_TABLE: Table = [
    (float("-inf"), "Underweight", "< 18.5 kg/m\u00b2"),
    (18.5,          "Normal",      "18.5-24.9 kg/m\u00b2"),
    (25,            "Overweight",  "25-29.9 kg/m\u00b2"),
    (30,            "Obese",       ">= 30 kg/m\u00b2"),
]

_BMI_SOUTH_ASIAN_SOURCE = "WHO Expert Consultation on BMI in Asian Populations (2004)"
_BMI_SOUTH_ASIAN_TABLE: Table = [
    (float("-inf"), "Normal",         "< 23 kg/m\u00b2"),
    (23,            "Increased risk", "23-27.4 kg/m\u00b2"),
    (27.5,          "High risk",      ">= 27.5 kg/m\u00b2"),
]

# Non-sex-specific, non-BMI biomarkers
_TABLE_MAP: dict[str, tuple[Table, str]] = {
    "LDL":   (_LDL_TABLE, _LDL_SOURCE),
    "TG":    (_TG_TABLE, _TG_SOURCE),
    "TC":    (_TC_TABLE, _TC_SOURCE),
    "HbA1c": (_HBA1C_TABLE, _HBA1C_SOURCE),
    "FPG":   (_FPG_TABLE, _FPG_SOURCE),
    "SBP":   (_SBP_TABLE, _BP_SOURCE),
    "DBP":   (_DBP_TABLE, _BP_SOURCE),
}

# Biomarkers affected by each medication flag (docs/CLINICAL_LOGIC_APPENDIX.md "Medication Notes")
_MED_AFFECTS: dict[str, set[str]] = {
    "chol_med": {"LDL", "HDL", "TG", "TC"},
    "bp_med":   {"SBP", "DBP"},
    "insulin":  {"HbA1c", "FPG"},
    "dm_pills": {"HbA1c", "FPG"},
}


# ---------------------------------------------------------------------------
# Core classification
# ---------------------------------------------------------------------------

def _classify(value: float, table: Table) -> tuple[str, str]:
    """Return (category, range_description) for value using an ascending table."""
    category, range_desc = table[0][1], table[0][2]
    for lower_bound, cat, rdesc in table:
        if value >= lower_bound:
            category, range_desc = cat, rdesc
        else:
            break
    return category, range_desc


def classify_bmi_south_asian(value: float) -> tuple[str, str]:
    """
    Classify a BMI value using South Asian context thresholds
    (WHO Expert Consultation 2004). Separate from classify_all_biomarkers,
    which uses the standard WHO table for the BMI threshold_results entry.
    Used by south_asian_context.get_south_asian_context().
    """
    return _classify(value, _BMI_SOUTH_ASIAN_TABLE)


def _medication_note_for(label: str, data) -> str | None:
    """Short per-biomarker note if any active medication flag affects this biomarker."""
    active = [flag for flag, affected in _MED_AFFECTS.items() if label in affected and get_field(data, flag)]
    if not active:
        return None
    return "May reflect medication effects \u2014 see medication notes."


def classify_all_biomarkers(data) -> list[dict]:
    """
    data: a BiomarkerInput instance or an equivalent dict (see
    api/models/patient.py for field names).

    Returns a list of ThresholdResult-shaped dicts (api/models/results.py),
    one per biomarker in BIOMARKERS order. For biomarkers with a None input
    value, category is None and category_description explains the value is
    not provided \u2014 these are also reported in find_missing_biomarkers().

    HDL uses sex-specific thresholds (sex field, 'M' or 'F'; defaults to 'M'
    table if sex is None \u2014 see docs/CLINICAL_LOGIC_APPENDIX.md HDL section).
    BMI uses the STANDARD WHO table here; South Asian context is a separate
    panel produced by south_asian_context.get_south_asian_context().
    """
    results: list[dict] = []

    for spec in BIOMARKERS:
        value = get_field(data, spec.input_field)

        if spec.label == "HDL":
            sex = get_field(data, "sex")
            table = _HDL_FEMALE_TABLE if sex == "F" else _HDL_MALE_TABLE
            source = _HDL_SOURCE
        elif spec.label == "BMI":
            table, source = _BMI_STANDARD_TABLE, _BMI_STANDARD_SOURCE
        else:
            table, source = _TABLE_MAP[spec.label]

        if value is None:
            results.append({
                "biomarker": spec.label,
                "value": None,
                "unit": spec.unit,
                "category": None,
                "category_description": "Not provided",
                "guideline_source": source,
                "note": None,
            })
            continue

        category, range_desc = _classify(value, table)
        results.append({
            "biomarker": spec.label,
            "value": value,
            "unit": spec.unit,
            "category": category,
            "category_description": f"{category} ({range_desc})",
            "guideline_source": source,
            "note": _medication_note_for(spec.label, data),
        })

    return results


# ---------------------------------------------------------------------------
# GET /api/v1/thresholds support
# ---------------------------------------------------------------------------

def _table_to_categories(table: Table, source: str, suffix: str = "") -> list[dict]:
    return [
        {"category": f"{cat}{suffix}", "range_description": rdesc, "guideline_source": source}
        for _, cat, rdesc in table
    ]


def get_all_threshold_categories() -> dict:
    """
    Returns a dict matching ThresholdsResponse (api/models/results.py) exactly:
    LDL, HDL, TG, TC, HbA1c, FPG, SBP, DBP, BMI_standard, BMI_south_asian_context.

    HDL is sex-specific in CLINICAL_LOGIC_APPENDIX.md, so both male and female
    category sets are returned with a "(Male)" / "(Female)" suffix on the
    category name \u2014 ThresholdCategory has no separate sex field.
    """
    hdl_categories = (
        _table_to_categories(_HDL_MALE_TABLE, _HDL_SOURCE, suffix=" (Male)")
        + _table_to_categories(_HDL_FEMALE_TABLE, _HDL_SOURCE, suffix=" (Female)")
    )

    return {
        "LDL": _table_to_categories(_LDL_TABLE, _LDL_SOURCE),
        "HDL": hdl_categories,
        "TG": _table_to_categories(_TG_TABLE, _TG_SOURCE),
        "TC": _table_to_categories(_TC_TABLE, _TC_SOURCE),
        "HbA1c": _table_to_categories(_HBA1C_TABLE, _HBA1C_SOURCE),
        "FPG": _table_to_categories(_FPG_TABLE, _FPG_SOURCE),
        "SBP": _table_to_categories(_SBP_TABLE, _BP_SOURCE),
        "DBP": _table_to_categories(_DBP_TABLE, _BP_SOURCE),
        "BMI_standard": _table_to_categories(_BMI_STANDARD_TABLE, _BMI_STANDARD_SOURCE),
        "BMI_south_asian_context": _table_to_categories(_BMI_SOUTH_ASIAN_TABLE, _BMI_SOUTH_ASIAN_SOURCE),
    }


def medication_affects() -> dict[str, set[str]]:
    """Public accessor for the medication -> affected-biomarker map (single
    source of truth; reused by sahc_risklens/trajectory/analytics.py)."""
    return {flag: set(bms) for flag, bms in _MED_AFFECTS.items()}


__all__ = [
    "medication_affects",
    "classify_all_biomarkers",
    "classify_bmi_south_asian",
    "get_all_threshold_categories",
    "find_missing_biomarkers",
]
