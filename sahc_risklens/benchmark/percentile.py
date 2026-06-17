"""
sahc_risklens/benchmark/percentile.py

Builds the NHANES Non-Hispanic Asian benchmark: for each biomarker, the cohort
p10 / p25 / median / p75 / p90 and the cohort sample size, plus the patient's
own value placed against that distribution.

Data source resolution:
  - If the real NHANES XPT files are present (nhanes_loader.nhanes_files_available),
    percentiles are computed from the live Non-Hispanic Asian cohort.
  - Otherwise the frozen demo percentiles (sahc_risklens/data/demo_cohort.py,
    which are the same real numbers) are used.

Output dicts are shaped exactly like api/models/results.py BenchmarkPoint:
    biomarker, patient_value, cohort_p10, cohort_p25, cohort_median,
    cohort_p75, cohort_p90, cohort_label, cohort_n

cohort_label is always config.NHANES_COHORT_LABEL.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from sahc_risklens.clinical.biomarkers import get_biomarker_spec, get_field
from sahc_risklens.config import NHANES_COHORT_LABEL
from sahc_risklens.data.demo_cohort import get_demo_percentiles
from sahc_risklens.data.nhanes_loader import (
    BIOMARKER_KEYS,
    load_biomarker_frame,
    nhanes_files_available,
)

# Minimum non-missing cohort values for a biomarker to be benchmarked.
MIN_COHORT_N = 30

_PERCENTILE_POINTS = (10, 25, 50, 75, 90)


def _percentiles_from_frame() -> dict[str, dict[str, float]]:
    """Compute p10/p25/median/p75/p90 + n per biomarker from the live cohort."""
    frame = load_biomarker_frame()
    table: dict[str, dict[str, float]] = {}
    for key in BIOMARKER_KEYS:
        if key not in frame.columns:
            continue
        series = frame[key].dropna()
        if len(series) < MIN_COHORT_N:
            continue
        p10, p25, p50, p75, p90 = np.percentile(series, _PERCENTILE_POINTS)
        table[key] = {
            "p10": round(float(p10), 1),
            "p25": round(float(p25), 1),
            "median": round(float(p50), 1),
            "p75": round(float(p75), 1),
            "p90": round(float(p90), 1),
            "n": int(len(series)),
        }
    return table


@lru_cache(maxsize=1)
def get_cohort_percentiles() -> dict[str, dict[str, float]]:
    """
    Return the cohort percentile table, computed from real NHANES files when
    available, otherwise the frozen demo table. Cached for the process lifetime
    (the underlying data does not change at runtime).
    """
    if nhanes_files_available():
        table = _percentiles_from_frame()
        if table:
            return table
    return get_demo_percentiles()


def get_benchmark_data(data) -> list[dict]:
    """
    data: a BiomarkerInput instance or equivalent dict.

    Returns a list of BenchmarkPoint-shaped dicts, one per biomarker that has a
    cohort benchmark, in canonical biomarker order. patient_value is the
    patient's input for that biomarker (may be None); the cohort fields always
    carry the reference distribution so the frontend can plot the distribution
    even when the patient left a field blank.
    """
    percentiles = get_cohort_percentiles()
    points: list[dict] = []

    for key in BIOMARKER_KEYS:
        stats = percentiles.get(key)
        if stats is None:
            continue
        spec = get_biomarker_spec(key)
        patient_value = get_field(data, spec.input_field)
        points.append({
            "biomarker": key,
            "patient_value": patient_value,
            "cohort_p10": stats["p10"],
            "cohort_p25": stats["p25"],
            "cohort_median": stats["median"],
            "cohort_p75": stats["p75"],
            "cohort_p90": stats["p90"],
            "cohort_label": NHANES_COHORT_LABEL,
            "cohort_n": int(stats["n"]),
        })
    return points


def percentile_rank(value: float, key: str) -> float | None:
    """
    Approximate percentile rank (0-100) of `value` within the cohort, by linear
    interpolation across the stored p10/p25/median/p75/p90 anchors. Returns None
    if the biomarker has no benchmark. Intended for descriptive context only, not
    clinical classification (that is thresholds.py).
    """
    stats = get_cohort_percentiles().get(key)
    if stats is None:
        return None
    anchors = [
        (stats["p10"], 10.0), (stats["p25"], 25.0), (stats["median"], 50.0),
        (stats["p75"], 75.0), (stats["p90"], 90.0),
    ]
    if value <= anchors[0][0]:
        return 10.0
    if value >= anchors[-1][0]:
        return 90.0
    for (v_lo, p_lo), (v_hi, p_hi) in zip(anchors, anchors[1:]):
        if v_lo <= value <= v_hi:
            if v_hi == v_lo:
                return round(p_lo, 1)
            frac = (value - v_lo) / (v_hi - v_lo)
            return round(p_lo + frac * (p_hi - p_lo), 1)
    return None


__all__ = [
    "MIN_COHORT_N",
    "get_cohort_percentiles",
    "get_benchmark_data",
    "percentile_rank",
]
