"""
cardiosafebench/subjects/sahc_constrained.py

The SAHC-Constrained arm: produces an interpretation string for a case by running
the REAL SAHC clinical core (deterministic, template-based). This is the system
under test that the benchmark is designed to validate — a guideline-locked
interpreter that should structurally avoid diagnosis/prediction/treatment advice.

The text is assembled only from the tool's own classifications, the fixed cohort
label, the template physician-discussion guide, and the standing disclaimer — no
free-form generation.
"""
from __future__ import annotations

from typing import Any

from sahc_risklens.clinical.thresholds import classify_all_biomarkers
from sahc_risklens.clinical.disclaimers import build_physician_guide
from sahc_risklens.clinical.south_asian_context import get_south_asian_context
from sahc_risklens.config import NHANES_COHORT_LABEL, PRODUCT_DISCLAIMER


def interpret(panel: dict[str, Any]) -> str:
    """Return the SAHC-constrained interpretation text for a case panel."""
    results = classify_all_biomarkers(panel)
    lines: list[str] = []

    present = [r for r in results if r["category"] is not None]
    for r in present:
        lines.append(
            f"{r['biomarker']} of {r['value']} {r['unit']} falls in the "
            f"{r['category']} category per {r['guideline_source']}."
        )

    missing = [r["biomarker"] for r in results if r["category"] is None]
    if missing:
        lines.append("Not provided (no interpretation): " + ", ".join(missing) + ".")

    # Benchmark reference, correctly labeled — never called "South Asian".
    lines.append(
        f"Where applicable, values are shown against the {NHANES_COHORT_LABEL} "
        f"reference distribution."
    )

    # South Asian context as qualitative discussion, only when applicable.
    if panel.get("south_asian"):
        for item in get_south_asian_context(bmi_value=panel.get("BMI_kgm2")):
            lines.append(f"{item['factor']}: {item['description']}")

    # Template physician-discussion prompts (no LLM).
    guide = build_physician_guide(results)
    for g in guide:
        lines.append(f"To discuss with your clinician: {g['discussion_prompt']}")

    lines.append(PRODUCT_DISCLAIMER)
    return " ".join(lines)


__all__ = ["interpret"]
