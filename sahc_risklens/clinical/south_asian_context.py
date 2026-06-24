"""
sahc_risklens/clinical/south_asian_context.py

South Asian risk-enhancing context panel.

SOURCE OF TRUTH: docs/CLINICAL_LOGIC_APPENDIX.md
  - "South Asian ASCVD Risk Context" section (2018 AHA/ACC Cholesterol Guideline)
  - "BMI \u2014 South Asian Context" section (WHO Expert Consultation 2004)

Per docs/CLINICAL_LOGIC_APPENDIX.md: "Do not quantify individual risk \u2014 present
as qualitative risk-enhancing factor." This module contains static, guideline-backed
text only. It does not call an LLM and does not produce a numeric risk score.

The caller (api/routers/benchmark.py, in P3) decides whether to include this
panel at all \u2014 typically only when BiomarkerInput.south_asian is True.
"""
from __future__ import annotations

from sahc_risklens.clinical.thresholds import classify_bmi_south_asian

_ASCVD_SOURCE = "2018 AHA/ACC Cholesterol Guideline"
_BMI_SOUTH_ASIAN_SOURCE = "WHO Expert Consultation on BMI in Asian Populations (2004)"


def get_south_asian_context(bmi_value: float | None = None,
                            lpa_value: float | None = None) -> list[dict]:
    """
    Returns a list of SouthAsianContextItem-shaped dicts
    (factor, description, guideline_source) per api/models/results.py.

    Always includes the ASCVD risk-enhancing factor item (qualitative).
    Includes a BMI-specific item only when bmi_value is provided \u2014
    its category is computed via classify_bmi_south_asian (South Asian
    thresholds, separate from the standard WHO BMI category shown in
    threshold_results).
    """
    items: list[dict] = [
        {
            "factor": "South Asian Ancestry \u2014 ASCVD Risk-Enhancing Factor",
            "description": (
                "South Asian ancestry is recognized as a risk-enhancing factor in the "
                "2018 AHA/ACC Cholesterol Guideline. South Asians may have elevated "
                "atherosclerotic cardiovascular disease (ASCVD) risk compared with "
                "other populations, and this risk may be underestimated by standard "
                "risk calculators. This is guideline-based clinical context for "
                "discussion with your physician \u2014 not an individual risk score."
            ),
            "guideline_source": _ASCVD_SOURCE,
        }
    ]

    if lpa_value is not None and lpa_value >= 50:
        items.append({
            "factor": "Lipoprotein(a) — South Asian Context",
            "description": (
                f"Your Lp(a) of {lpa_value} mg/dL is at or above the 50 mg/dL "
                f"(125 nmol/L) threshold the 2018 AHA/ACC Cholesterol Guideline "
                f"recognizes as a risk-enhancing factor. Lp(a) is largely "
                f"genetically determined and tends to be elevated more often in "
                f"South Asian populations. This is qualitative context for "
                f"discussion with your physician — not an individual risk score."
            ),
            "guideline_source": _ASCVD_SOURCE,
        })

    if bmi_value is not None:
        category, range_desc = classify_bmi_south_asian(bmi_value)
        items.append({
            "factor": "BMI \u2014 South Asian Context",
            "description": (
                f"Your BMI of {bmi_value} kg/m\u00b2 falls in the '{category}' category "
                f"({range_desc}) using BMI thresholds specific to South Asian "
                f"populations (WHO Expert Consultation 2004). These thresholds are "
                f"lower than standard WHO categories and are shown here as additional "
                f"risk-context \u2014 not as part of the NHANES Non-Hispanic Asian benchmark."
            ),
            "guideline_source": _BMI_SOUTH_ASIAN_SOURCE,
        })

    return items


__all__ = ["get_south_asian_context"]
