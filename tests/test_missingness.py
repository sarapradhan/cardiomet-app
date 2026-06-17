"""
tests/test_missingness.py

Tests for sahc_risklens/data/missingness.py. Verifies counts/percentages and the
rule that nothing is imputed or dropped.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from sahc_risklens.data.missingness import (
    columns_below_threshold,
    missingness_report,
)


def _df() -> pd.DataFrame:
    return pd.DataFrame({
        "A": [1, 2, 3, 4],          # 0 missing
        "B": [1, np.nan, 3, np.nan],  # 2 missing
        "C": [np.nan, np.nan, np.nan, np.nan],  # all missing
    })


def test_report_counts_present_and_missing():
    rep = missingness_report(_df())
    assert rep["A"] == {"n_total": 4, "n_present": 4, "n_missing": 0, "pct_missing": 0.0}
    assert rep["B"]["n_missing"] == 2
    assert rep["B"]["pct_missing"] == 50.0
    assert rep["C"]["pct_missing"] == 100.0


def test_report_specific_columns_only():
    rep = missingness_report(_df(), columns=["B"])
    assert set(rep.keys()) == {"B"}


def test_report_absent_column_reported_as_fully_missing():
    rep = missingness_report(_df(), columns=["DOES_NOT_EXIST"])
    assert rep["DOES_NOT_EXIST"]["pct_missing"] == 100.0
    assert rep["DOES_NOT_EXIST"]["n_present"] == 0


def test_report_does_not_mutate_or_impute():
    df = _df()
    _ = missingness_report(df)
    # B still has its NaNs — nothing filled
    assert df["B"].isna().sum() == 2


def test_columns_below_threshold():
    below = columns_below_threshold(_df(), min_present=3)
    # A has 4 present (ok), B has 2 (<3), C has 0 (<3)
    assert "A" not in below
    assert "B" in below
    assert "C" in below


def test_empty_frame_pct_zero():
    rep = missingness_report(pd.DataFrame({"A": []}))
    assert rep["A"]["pct_missing"] == 0.0
    assert rep["A"]["n_total"] == 0
