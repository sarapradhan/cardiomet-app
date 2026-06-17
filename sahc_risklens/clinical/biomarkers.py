"""
sahc_risklens/clinical/biomarkers.py

Biomarker schema — single source of truth for the mapping between the two
naming conventions used across this system:

- Input fields (api/models/patient.py BiomarkerInput): include a unit suffix,
  e.g. LDL_mgdl, HbA1c_pct, BMI_kgm2
- Output labels (api/models/results.py ThresholdResult.biomarker): short
  clinical name, e.g. LDL, HbA1c, BMI — this is what
  tests/test_api_endpoints.py _find() searches on

All other clinical modules import BIOMARKERS from here rather than
hardcoding field names.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class BiomarkerSpec:
    """Metadata for a single biomarker."""
    label: str          # short output label, e.g. "LDL" — matches ThresholdResult.biomarker
    input_field: str     # BiomarkerInput field name, e.g. "LDL_mgdl"
    unit: str            # display unit, e.g. "mg/dL"
    full_name: str       # human-readable name, e.g. "LDL Cholesterol"
    sex_specific: bool = False


# Ordered registry — order determines display order in threshold_results.
# Source: docs/DATA_DICTIONARY.md (input fields) and docs/CLINICAL_LOGIC_APPENDIX.md (units/sources)
BIOMARKERS: list[BiomarkerSpec] = [
    BiomarkerSpec(label="LDL",   input_field="LDL_mgdl",  unit="mg/dL", full_name="LDL Cholesterol"),
    BiomarkerSpec(label="HDL",   input_field="HDL_mgdl",  unit="mg/dL", full_name="HDL Cholesterol", sex_specific=True),
    BiomarkerSpec(label="TG",    input_field="TG_mgdl",   unit="mg/dL", full_name="Triglycerides"),
    BiomarkerSpec(label="TC",    input_field="TC_mgdl",   unit="mg/dL", full_name="Total Cholesterol"),
    BiomarkerSpec(label="HbA1c", input_field="HbA1c_pct", unit="%",     full_name="HbA1c"),
    BiomarkerSpec(label="FPG",   input_field="FPG_mgdl",  unit="mg/dL", full_name="Fasting Plasma Glucose"),
    BiomarkerSpec(label="SBP",   input_field="SBP_mmhg",  unit="mm Hg", full_name="Systolic Blood Pressure"),
    BiomarkerSpec(label="DBP",   input_field="DBP_mmhg",  unit="mm Hg", full_name="Diastolic Blood Pressure"),
    BiomarkerSpec(label="BMI",   input_field="BMI_kgm2",  unit="kg/m\u00b2", full_name="BMI"),
]

# Demographic / medication fields — never treated as biomarkers for
# missing_biomarkers purposes.
NON_BIOMARKER_FIELDS = {"age_yr", "sex", "south_asian", "bp_med", "chol_med", "insulin", "dm_pills"}


def get_biomarker_spec(label: str) -> BiomarkerSpec:
    """Look up a BiomarkerSpec by its short output label (e.g. 'LDL')."""
    for spec in BIOMARKERS:
        if spec.label == label:
            return spec
    raise KeyError(f"Unknown biomarker label: {label!r}")


def get_field(data, name: str, default=None):
    """
    Read a field from `data`, whether it's a dict or an object with attributes
    (e.g. a Pydantic BiomarkerInput instance). Used throughout sahc_risklens/clinical/
    so the same functions work with raw dicts (tests) and BiomarkerInput (API).
    """
    if isinstance(data, dict):
        return data.get(name, default)
    return getattr(data, name, default)


def find_missing_biomarkers(data) -> list[str]:
    """
    Return input field names (e.g. 'HbA1c_pct') for every biomarker whose
    value is None. Matches the field-name convention expected by
    BenchmarkResponse.missing_biomarkers (see tests/test_api_endpoints.py
    test_missing_hba1c_flagged).
    """
    return [spec.input_field for spec in BIOMARKERS if get_field(data, spec.input_field) is None]
