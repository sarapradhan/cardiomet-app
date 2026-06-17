"""
sahc_risklens/data/cohort_filters.py

NHANES cohort filtering. Source of truth: docs/DATA_DICTIONARY.md.

Two filters:
  - filter_non_hispanic_asian: RIDRETH3 == 6, the only cohort this tool reports
    on (always labeled "NHANES Non-Hispanic Asian" elsewhere).
  - apply_fasting_filter: fasting plasma glucose is only valid for participants
    fasted >= 8 hours (PHAFSTHR). Non-fasting rows have their glucose value set
    to NaN rather than being dropped, so the participant still contributes their
    other biomarkers to the cohort.
"""
from __future__ import annotations

import pandas as pd


def filter_non_hispanic_asian(df: pd.DataFrame, ridreth3_value: int = 6) -> pd.DataFrame:
    """
    Return only rows where RIDRETH3 == ridreth3_value (default 6 = Non-Hispanic
    Asian). Raises if RIDRETH3 is absent, so a mis-joined frame fails loudly
    rather than returning everyone.
    """
    if "RIDRETH3" not in df.columns:
        raise ValueError("RIDRETH3 column not present; cannot apply cohort filter")
    return df[df["RIDRETH3"] == ridreth3_value].copy()


def apply_fasting_filter(
    df: pd.DataFrame,
    fasting_col: str = "PHAFSTHR",
    glucose_col: str = "LBXGLU",
    min_hours: float = 8,
) -> pd.DataFrame:
    """
    Invalidate (set to NaN) fasting plasma glucose for rows that did not meet the
    minimum fasting duration. Rows are NOT dropped — only the glucose value is
    cleared — because the participant's other biomarkers remain valid.

    If either column is missing the frame is returned unchanged (e.g. a frame
    that never carried glucose), since there is nothing to invalidate.
    """
    if fasting_col not in df.columns or glucose_col not in df.columns:
        return df.copy()

    out = df.copy()
    not_fasting = out[fasting_col].isna() | (out[fasting_col] < min_hours)
    out.loc[not_fasting, glucose_col] = pd.NA
    return out


__all__ = ["filter_non_hispanic_asian", "apply_fasting_filter"]
