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

PRODUCT_DISCLAIMER = (
    "This tool provides educational benchmarking context only. "
    "It does not diagnose, prescribe, or replace clinical judgment. "
    "Discuss all results with a qualified clinician."
)
