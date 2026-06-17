"""
sahc_risklens/data/missingness.py

Missingness reporting. Source-of-truth rule (docs/DATA_DICTIONARY.md): report all
missing values; never silently drop or impute. This module only measures and
reports — it never fills.

High missingness is expected and normal for some variables (e.g. fasting glucose
is a morning subsample), so a high rate is information, not an error.
"""
from __future__ import annotations

import pandas as pd


def missingness_report(df: pd.DataFrame, columns: list[str] | None = None) -> dict[str, dict]:
    """
    For each column (default: all), return a dict with:
      n_total, n_present, n_missing, pct_missing (0-100, rounded to 1 dp).

    Returns {column: {...}, ...}. A missing requested column is reported with
    n_total == n_present == 0 and pct_missing == 100.0, so callers can detect a
    variable that was never joined in without a KeyError.
    """
    cols = columns if columns is not None else list(df.columns)
    n_total = len(df)
    report: dict[str, dict] = {}

    for col in cols:
        if col not in df.columns:
            report[col] = {"n_total": 0, "n_present": 0, "n_missing": 0, "pct_missing": 100.0}
            continue
        n_present = int(df[col].notna().sum())
        n_missing = n_total - n_present
        pct = round(100.0 * n_missing / n_total, 1) if n_total else 0.0
        report[col] = {
            "n_total": n_total,
            "n_present": n_present,
            "n_missing": n_missing,
            "pct_missing": pct,
        }
    return report


def columns_below_threshold(
    df: pd.DataFrame, min_present: int, columns: list[str] | None = None
) -> list[str]:
    """
    Return columns with fewer than `min_present` non-missing values. Useful for
    flagging biomarkers whose cohort sample is too small for a stable percentile
    benchmark (see sahc_risklens/benchmark/percentile.py).
    """
    report = missingness_report(df, columns)
    return [col for col, stats in report.items() if stats["n_present"] < min_present]


__all__ = ["missingness_report", "columns_below_threshold"]
