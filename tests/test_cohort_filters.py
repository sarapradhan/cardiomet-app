"""
tests/test_cohort_filters.py

Tests for sahc_risklens/data/cohort_filters.py. Uses small in-memory DataFrames
so the logic is verified independently of the real NHANES files.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sahc_risklens.data.cohort_filters import (
    apply_fasting_filter,
    filter_non_hispanic_asian,
)


def _demo_df() -> pd.DataFrame:
    return pd.DataFrame({
        "SEQN": [1, 2, 3, 4, 5],
        "RIDRETH3": [6, 3, 6, 4, 6],   # three NH-Asian (6), two others
        "LBXGLU": [95, 110, 88, 130, 102],
        "PHAFSTHR": [9.0, 10.0, 3.0, np.nan, 8.0],
    })


def test_filter_keeps_only_ridreth3_6():
    out = filter_non_hispanic_asian(_demo_df(), ridreth3_value=6)
    assert len(out) == 3
    assert set(out["SEQN"]) == {1, 3, 5}
    assert (out["RIDRETH3"] == 6).all()


def test_filter_does_not_mutate_input():
    df = _demo_df()
    _ = filter_non_hispanic_asian(df)
    assert len(df) == 5  # original unchanged


def test_filter_raises_without_ridreth3():
    df = pd.DataFrame({"SEQN": [1, 2], "LBXGLU": [90, 100]})
    with pytest.raises(ValueError, match="RIDRETH3"):
        filter_non_hispanic_asian(df)


def test_fasting_filter_clears_non_fasting_glucose():
    out = apply_fasting_filter(_demo_df(), min_hours=8)
    by_seqn = out.set_index("SEQN")["LBXGLU"]
    # SEQN 1 (9h) and 5 (8h) keep glucose; 2 (10h) keeps; 3 (3h) and 4 (NaN hrs) cleared
    assert by_seqn[1] == 95
    assert by_seqn[2] == 110
    assert by_seqn[5] == 102
    assert pd.isna(by_seqn[3])
    assert pd.isna(by_seqn[4])


def test_fasting_filter_keeps_all_rows():
    """Non-fasting rows are retained (only glucose cleared), not dropped."""
    out = apply_fasting_filter(_demo_df(), min_hours=8)
    assert len(out) == 5


def test_fasting_filter_boundary_exactly_8_hours_is_valid():
    df = pd.DataFrame({"SEQN": [1], "LBXGLU": [100.0], "PHAFSTHR": [8.0]})
    out = apply_fasting_filter(df, min_hours=8)
    assert out.loc[0, "LBXGLU"] == 100.0


def test_fasting_filter_just_under_8_hours_is_invalid():
    df = pd.DataFrame({"SEQN": [1], "LBXGLU": [100.0], "PHAFSTHR": [7.9]})
    out = apply_fasting_filter(df, min_hours=8)
    assert pd.isna(out.loc[0, "LBXGLU"])


def test_fasting_filter_missing_columns_noop():
    df = pd.DataFrame({"SEQN": [1, 2], "LBXTC": [180, 200]})
    out = apply_fasting_filter(df)
    pd.testing.assert_frame_equal(out, df)
