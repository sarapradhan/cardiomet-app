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
# labeled "South Asian"; the SAHC cohort is a genuine South Asian clinical
# cohort and carries its own proper-noun label. Keeping them as two distinct,
# separately-labeled cohorts preserves the proxy-vs-actual distinction that is
# the intellectual core of this project (see docs/SAHC_COHORT.md).
COHORT_NHANES = "nhanes_asian"
COHORT_SAHC   = "sahc"
DEFAULT_COHORT = COHORT_NHANES   # default preserves existing behavior/contract

# SAHC clinic cohort: South Asian patients only (RIDRETH3 == 1 in the source file).
SAHC_COHORT_RIDRETH3_VALUE = 1
SAHC_COHORT_LABEL = "South Asian Heart Center clinical cohort"
SAHC_DATA_DIR  = Path(os.getenv("SAHC_DATA_DIR", str(ROOT_DIR / "data" / "sahc")))
SAHC_DATA_FILE = SAHC_DATA_DIR / "sahc_cohort_noPID.csv"

COHORT_LABELS: dict[str, str] = {
    COHORT_NHANES: NHANES_COHORT_LABEL,
    COHORT_SAHC:   SAHC_COHORT_LABEL,
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
