"""
sahc_risklens/clinical/disclaimers.py

Template-based physician discussion guide and medication notes.

Phase 1 rule (CONTRIBUTING.md, docs/PRD.md Section 7\u20138): physician discussion guide
is rule-based template output ONLY. No LLM calls anywhere in this module.
Every string here is a fixed template with values substituted in \u2014 nothing
is generated.

SOURCE OF TRUTH for medication note wording: docs/CLINICAL_LOGIC_APPENDIX.md
"Medication Notes" section. Medication status does NOT adjust threshold
classifications (Phase 1 rule) \u2014 it is surfaced as a separate note only.
"""
from __future__ import annotations

from sahc_risklens.clinical.biomarkers import get_biomarker_spec, get_field

# Categories considered "not elevated" \u2014 excluded from the physician guide.
# Every other non-None category (Near Optimal/Borderline/High/.../Stages/Increased risk/etc.)
# is included.
_LOWEST_RISK_CATEGORIES = {"Optimal", "Normal", "Desirable", "Protective"}

# field -> (human label, biomarkers affected) \u2014 matches
# docs/CLINICAL_LOGIC_APPENDIX.md "Medication Notes" and
# sahc_risklens/clinical/thresholds._MED_AFFECTS
_MEDICATION_LABELS: dict[str, str] = {
    "chol_med": "cholesterol medication",
    "bp_med":   "blood pressure medication",
    "insulin":  "insulin",
    "dm_pills": "diabetes medication",
}


def build_physician_guide(threshold_results: list[dict]) -> list[dict]:
    """
    threshold_results: output of thresholds.classify_all_biomarkers().

    Returns a list of PhysicianGuideItem-shaped dicts
    (biomarker, category, discussion_prompt, guideline_note) per
    api/models/results.py.

    Only biomarkers with a present value (category is not None) AND a
    category outside _LOWEST_RISK_CATEGORIES are included \u2014 i.e. results
    that are worth a discussion prompt. Template text only; no LLM call.
    """
    items: list[dict] = []

    for result in threshold_results:
        category = result["category"]
        if category is None or category in _LOWEST_RISK_CATEGORIES:
            continue

        spec = get_biomarker_spec(result["biomarker"])
        items.append({
            "biomarker": result["biomarker"],
            "category": category,
            "discussion_prompt": (
                f"Your {spec.full_name} is {result['value']} {result['unit']}, "
                f"classified as {result['category_description']}. "
                f"You may want to ask your clinician what this means for you "
                f"and whether any follow-up is recommended."
            ),
            "guideline_note": f"Reference: {result['guideline_source']}.",
        })

    return items


def get_medication_notes(data) -> list[str]:
    """
    data: a BiomarkerInput instance or equivalent dict.

    Returns one note per active medication flag (bp_med, chol_med, insulin,
    dm_pills), per docs/CLINICAL_LOGIC_APPENDIX.md "Medication Notes".
    Returns [] when no medication flags are set.

    Does NOT adjust any threshold classification \u2014 Phase 1 rule.
    """
    notes: list[str] = []
    for field, label in _MEDICATION_LABELS.items():
        if get_field(data, field):
            notes.append(
                f"Note: You indicated you are taking {label}. Your related "
                f"values may reflect medication effects. Discuss interpretation "
                f"with your clinician."
            )
    return notes


__all__ = ["build_physician_guide", "get_medication_notes"]
