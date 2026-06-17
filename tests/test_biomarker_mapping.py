"""
tests/test_biomarker_mapping.py

Tests for sahc_risklens/data/nhanes_loader.py.

The loader's pure-logic pieces (BP averaging, biomarker renaming) are tested with
in-memory DataFrames and always run. The full real-file pipeline is tested only
when the NHANES XPT files are present (downloaded via scripts/download_nhanes.py);
those tests skip cleanly in environments without the data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sahc_risklens.data.nhanes_loader import (
    BIOMARKER_KEYS,
    add_bp_means,
    load_biomarker_frame,
    nhanes_files_available,
    rename_to_biomarker_keys,
)

_NHANES = nhanes_files_available()
_requires_nhanes = pytest.mark.skipif(not _NHANES, reason="NHANES XPT files not present")


# ---------------------------------------------------------------------------
# Pure-logic tests (always run)
# ---------------------------------------------------------------------------

def test_biomarker_keys_canonical_set():
    assert BIOMARKER_KEYS == ["LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP", "BMI"]


def test_bp_means_average_three_readings():
    df = pd.DataFrame({
        "BPXSY1": [120, 130], "BPXSY2": [122, 132], "BPXSY3": [124, 134],
        "BPXDI1": [80, 90],   "BPXDI2": [82, 92],   "BPXDI3": [84, 94],
    })
    out = add_bp_means(df)
    assert out.loc[0, "SBP_mean"] == 122  # mean(120,122,124)
    assert out.loc[0, "DBP_mean"] == 82   # mean(80,82,84)
    assert out.loc[1, "SBP_mean"] == 132


def test_bp_means_ignore_nan():
    df = pd.DataFrame({
        "BPXSY1": [120.0], "BPXSY2": [np.nan], "BPXSY3": [124.0],
        "BPXDI1": [80.0],  "BPXDI2": [82.0],   "BPXDI3": [np.nan],
    })
    out = add_bp_means(df)
    assert out.loc[0, "SBP_mean"] == 122  # mean(120,124) ignoring NaN
    assert out.loc[0, "DBP_mean"] == 81   # mean(80,82)


def test_rename_to_biomarker_keys_maps_sources():
    cohort = pd.DataFrame({
        "LBDLDL": [100], "LBDHDD": [50], "LBXTR": [120], "LBXTC": [180],
        "LBXGH": [5.5], "LBXGLU": [95], "SBP_mean": [118], "DBP_mean": [76],
        "BMXBMI": [24.0],
    })
    out = rename_to_biomarker_keys(cohort)
    assert list(out.columns) == BIOMARKER_KEYS
    assert out.loc[0, "LDL"] == 100
    assert out.loc[0, "HbA1c"] == 5.5
    assert out.loc[0, "BMI"] == 24.0


# ---------------------------------------------------------------------------
# Real-file tests (skip without NHANES data)
# ---------------------------------------------------------------------------

@_requires_nhanes
def test_load_biomarker_frame_has_all_keys():
    frame = load_biomarker_frame()
    for key in BIOMARKER_KEYS:
        assert key in frame.columns, f"missing biomarker column: {key}"


@_requires_nhanes
def test_cohort_is_non_trivial_size():
    """NH-Asian cohort in 2017-2018 is ~1100+ participants."""
    frame = load_biomarker_frame()
    assert len(frame) > 500


@_requires_nhanes
def test_hba1c_present_in_cohort():
    """HbA1c (LBXGH) is required end-to-end and must have a real sample."""
    frame = load_biomarker_frame()
    assert frame["HbA1c"].notna().sum() > 100


@_requires_nhanes
def test_fpg_smaller_than_hba1c_sample():
    """FPG is a fasting subsample, so its n should be well below HbA1c's."""
    frame = load_biomarker_frame()
    assert frame["FPG"].notna().sum() < frame["HbA1c"].notna().sum()


@_requires_nhanes
def test_biomarker_values_in_plausible_ranges():
    """Sanity bounds — catches a units or column-mapping error."""
    frame = load_biomarker_frame()
    assert 40 <= frame["LDL"].median() <= 200
    assert 3.0 <= frame["HbA1c"].median() <= 9.0
    assert 15 <= frame["BMI"].median() <= 40
    assert 90 <= frame["SBP"].median() <= 150
