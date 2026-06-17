"""
sahc_risklens/data/nhanes_loader.py

Loads the NHANES 2017-2018 (_J) public XPT files, joins them on SEQN, applies
the cohort filter and fasting filter, computes averaged BP, and returns a clean
DataFrame keyed by the internal biomarker names used downstream.

SOURCE OF TRUTH for every file name, variable name, filter, and computed column:
docs/DATA_DICTIONARY.md. Do not introduce a variable here that is not in that
document.

This module reads real data only. When NHANES files are not present, the
application uses sahc_risklens/data/demo_cohort.py instead (see
sahc_risklens/benchmark/percentile.py, which chooses the source). Keeping the
real loader and the demo cohort in separate modules means the demo path never
silently masks a real-data bug.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from sahc_risklens.config import (
    FASTING_HOURS_MINIMUM,
    NHANES_COHORT_RIDRETH3_VALUE,
    NHANES_DATA_DIR,
)
from sahc_risklens.data.cohort_filters import (
    apply_fasting_filter,
    filter_non_hispanic_asian,
)

# File -> columns to pull (besides SEQN). Mirrors docs/DATA_DICTIONARY.md
# "File-to-Variable Summary".
_FILE_COLUMNS: dict[str, list[str]] = {
    "DEMO_J":   ["RIDAGEYR", "RIAGENDR", "RIDRETH3", "WTMEC2YR"],
    "TCHOL_J":  ["LBXTC"],
    "HDL_J":    ["LBDHDD"],
    "TRIGLY_J": ["LBDLDL", "LBXTR"],
    "GHB_J":    ["LBXGH"],
    "GLU_J":    ["LBXGLU"],
    "FASTQX_J": ["PHAFSTHR"],
    "BPX_J":    ["BPXSY1", "BPXSY2", "BPXSY3", "BPXDI1", "BPXDI2", "BPXDI3"],
    "BMX_J":    ["BMXBMI"],
    "BPQ_J":    ["BPQ050A", "BPQ090D"],
    "DIQ_J":    ["DIQ050", "DIQ070"],
}

# NHANES variable -> internal biomarker key (docs/DATA_DICTIONARY.md
# "Internal Biomarker Keys"). SBP/DBP map from the computed mean columns.
_BIOMARKER_SOURCE: dict[str, str] = {
    "LDL":   "LBDLDL",
    "HDL":   "LBDHDD",
    "TG":    "LBXTR",
    "TC":    "LBXTC",
    "HbA1c": "LBXGH",
    "FPG":   "LBXGLU",
    "SBP":   "SBP_mean",
    "DBP":   "DBP_mean",
    "BMI":   "BMXBMI",
}

# Internal biomarker keys, in canonical order.
BIOMARKER_KEYS: list[str] = list(_BIOMARKER_SOURCE.keys())


def nhanes_files_available(data_dir: Path | None = None) -> bool:
    """True if every required XPT file is present in data_dir."""
    base = Path(data_dir) if data_dir is not None else NHANES_DATA_DIR
    return all((base / f"{name}.XPT").exists() for name in _FILE_COLUMNS)


def _read_xpt(path: Path, columns: list[str]) -> pd.DataFrame:
    """Read SEQN + requested columns from one XPT file. Missing columns raise."""
    df = pd.read_sas(path, format="xport")
    df.columns = [str(c) for c in df.columns]
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing expected columns {missing}")
    keep = ["SEQN"] + columns
    return df[keep].copy()


def load_raw_merged(data_dir: Path | None = None) -> pd.DataFrame:
    """
    Read every file and outer-join on SEQN. No filtering, no computed columns.
    Useful for diagnostics and missingness reporting on the full sample.
    """
    base = Path(data_dir) if data_dir is not None else NHANES_DATA_DIR
    merged: pd.DataFrame | None = None
    for name, columns in _FILE_COLUMNS.items():
        df = _read_xpt(base / f"{name}.XPT", columns)
        merged = df if merged is None else merged.merge(df, on="SEQN", how="outer")
    assert merged is not None
    return merged


def add_bp_means(df: pd.DataFrame) -> pd.DataFrame:
    """Add SBP_mean / DBP_mean as the row-wise mean of the three readings (NaN-aware)."""
    out = df.copy()
    out["SBP_mean"] = out[["BPXSY1", "BPXSY2", "BPXSY3"]].mean(axis=1)
    out["DBP_mean"] = out[["BPXDI1", "BPXDI2", "BPXDI3"]].mean(axis=1)
    return out


def load_cohort(data_dir: Path | None = None) -> pd.DataFrame:
    """
    Full real-data pipeline:
      1. Merge all files on SEQN.
      2. Filter to RIDRETH3 == 6 (Non-Hispanic Asian).
      3. Add SBP_mean / DBP_mean.
      4. Apply the PHAFSTHR >= 8 fasting filter to FPG only (FPG is set to NaN
         for non-fasting rows; all other biomarkers are retained for those rows).

    Returns a DataFrame that still carries the internal-key columns produced by
    rename_to_biomarker_keys(); call that next to get LDL/HDL/.../BMI columns.
    """
    merged = load_raw_merged(data_dir)
    cohort = filter_non_hispanic_asian(merged, ridreth3_value=NHANES_COHORT_RIDRETH3_VALUE)
    cohort = add_bp_means(cohort)
    cohort = apply_fasting_filter(
        cohort, fasting_col="PHAFSTHR", glucose_col="LBXGLU", min_hours=FASTING_HOURS_MINIMUM
    )
    return cohort


def rename_to_biomarker_keys(cohort: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with one column per internal biomarker key
    (LDL, HDL, TG, TC, HbA1c, FPG, SBP, DBP, BMI), drawn from the NHANES
    source columns per docs/DATA_DICTIONARY.md.
    """
    data = {key: cohort[src] for key, src in _BIOMARKER_SOURCE.items() if src in cohort.columns}
    return pd.DataFrame(data)


def load_biomarker_frame(data_dir: Path | None = None) -> pd.DataFrame:
    """Convenience: load_cohort -> rename_to_biomarker_keys in one call."""
    return rename_to_biomarker_keys(load_cohort(data_dir))


__all__ = [
    "BIOMARKER_KEYS",
    "nhanes_files_available",
    "load_raw_merged",
    "add_bp_means",
    "load_cohort",
    "rename_to_biomarker_keys",
    "load_biomarker_frame",
]
