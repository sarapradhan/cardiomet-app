"""
sahc_risklens/config.py — Runtime configuration.
Import from here — never hardcode these values elsewhere.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR       = Path(__file__).resolve().parent.parent
NHANES_DATA_DIR = Path(os.getenv("NHANES_DATA_DIR", str(ROOT_DIR / "data" / "raw")))
MODE            = os.getenv("SAHC_MODE", "demo").lower()
IS_DEMO_MODE    = MODE == "demo" or not (NHANES_DATA_DIR / "DEMO_J.XPT").exists()

NHANES_CYCLE_SUFFIX      = "_J"
NHANES_CYCLE_YEARS       = "2017-2018"
NHANES_COHORT_RIDRETH3_VALUE = 6
NHANES_COHORT_LABEL      = "NHANES Non-Hispanic Asian"   # render this string everywhere
FASTING_HOURS_MINIMUM    = 8   # PHAFSTHR >= 8 for valid fasting glucose

# --- Selectable benchmark cohorts ---------------------------------------------
# The benchmark distribution a patient is compared against is a selectable
# dimension. Each cohort has a stable id (used in API params and cache keys) and
# an honest display label. The NHANES cohort is a population proxy and is NEVER
# labeled "South Asian".
#
# Exactly one cohort is registered today. A second cohort ("sahc") was removed
# on 2026-08-30 because its provenance could not be established; see
# docs/SAHC_COHORT.md for the full record. The multi-cohort machinery is
# deliberately retained — SUPPORTED_COHORTS, get_cohort_percentiles(cohort),
# the ?cohort= query parameter, and the peer-matching engine all still take a
# cohort id — so a properly sourced South Asian reference distribution can be
# registered here without reopening the architecture.
COHORT_NHANES = "nhanes_asian"
DEFAULT_COHORT = COHORT_NHANES

COHORT_LABELS: dict[str, str] = {
    COHORT_NHANES: NHANES_COHORT_LABEL,
}


def cohort_label(cohort: str) -> str:
    """Display label for a cohort id. Unknown ids raise (fail loud, never mislabel)."""
    try:
        return COHORT_LABELS[cohort]
    except KeyError as exc:
        raise ValueError(f"Unknown cohort id: {cohort!r}") from exc

PRODUCT_DISCLAIMER = (
    "This tool provides educational benchmarking context only. "
    "It does not diagnose, prescribe, or replace clinical judgment. "
    "Discuss all results with a qualified clinician."
)
