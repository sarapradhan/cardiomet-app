"""
sahc_risklens/data/sahc_cohort_loader.py

Loads the South Asian Heart Center (SAHC) de-identified clinical cohort and
returns a clean DataFrame keyed by the internal biomarker names used downstream
(LDL/HDL/TG/TC/HbA1c/FPG/SBP/DBP/BMI) — the same keys nhanes_loader produces, so
benchmark/percentile.py can treat both sources uniformly.

PROVENANCE & GOVERNANCE: docs/SAHC_COHORT.md. The raw patient CSV is NEVER
committed to git (see .gitignore: data/sahc/*.csv). When the file is absent the
application falls back to frozen aggregate percentiles in
sahc_risklens/data/sahc_demo_cohort.py, exactly mirroring how the NHANES loader
relates to demo_cohort.py.

Source schema (data/sahc/sahc_cohort_noPID.csv) already uses NHANES-style column
names:
    RIAGENDR, RIDRETH3, RIDAGEYR, LBXTC, LBXTR, LBDHDD, LBDLDL, TotHDLRat,
    LBXGLU, LBXGH, BMXBMI, BPXOSY1, BPXODI1, lab_or_exam, cholMeds, diabMeds,
    bpMeds, Age_Group

KNOWN DIFFERENCES vs the NHANES pipeline (documented, intentional):
  - Cohort filter is RIDRETH3 == 1 (the file's South Asian code), not == 6.
  - Blood pressure is a single oscillometric reading per patient
    (BPXOSY1 / BPXODI1); there is no three-reading average to compute.
  - Glucose (LBXGLU) has no fasting-hours field in this extract, so the fasting
    filter applied to NHANES FPG cannot be applied here. FPG percentiles for this
    cohort therefore include non-fasting draws — see docs/SAHC_COHORT.md.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from sahc_risklens.config import SAHC_COHORT_RIDRETH3_VALUE, SAHC_DATA_FILE

# NHANES-style source column -> internal biomarker key. Mirrors nhanes_loader's
# _BIOMARKER_SOURCE but uses the single-reading BP columns present in this file.
_BIOMARKER_SOURCE: dict[str, str] = {
    "LDL":   "LBDLDL",
    "HDL":   "LBDHDD",
    "TG":    "LBXTR",
    "TC":    "LBXTC",
    "HbA1c": "LBXGH",
    "FPG":   "LBXGLU",
    "SBP":   "BPXOSY1",
    "DBP":   "BPXODI1",
    "BMI":   "BMXBMI",
}

# Internal biomarker keys, in canonical order (identical to nhanes_loader).
BIOMARKER_KEYS: list[str] = list(_BIOMARKER_SOURCE.keys())


def sahc_file_available(data_file: Path | None = None) -> bool:
    """True if the raw SAHC cohort CSV is present (it is gitignored by design)."""
    path = Path(data_file) if data_file is not None else SAHC_DATA_FILE
    return path.exists()


def load_cohort(data_file: Path | None = None) -> pd.DataFrame:
    """
    Read the raw SAHC CSV and filter to the South Asian cohort
    (RIDRETH3 == SAHC_COHORT_RIDRETH3_VALUE). No renaming yet.
    """
    path = Path(data_file) if data_file is not None else SAHC_DATA_FILE
    df = pd.read_csv(path)
    df.columns = [str(c) for c in df.columns]
    if "RIDRETH3" in df.columns:
        df = df[df["RIDRETH3"] == SAHC_COHORT_RIDRETH3_VALUE]
    return df.copy()


def rename_to_biomarker_keys(cohort: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with one numeric column per internal biomarker key."""
    data = {
        key: pd.to_numeric(cohort[src], errors="coerce")
        for key, src in _BIOMARKER_SOURCE.items()
        if src in cohort.columns
    }
    return pd.DataFrame(data)


def load_biomarker_frame(data_file: Path | None = None) -> pd.DataFrame:
    """Convenience: load_cohort -> rename_to_biomarker_keys in one call."""
    return rename_to_biomarker_keys(load_cohort(data_file))


__all__ = [
    "BIOMARKER_KEYS",
    "sahc_file_available",
    "load_cohort",
    "rename_to_biomarker_keys",
    "load_biomarker_frame",
]
