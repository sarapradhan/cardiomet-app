"""
sahc_risklens/benchmark/percentile.py

Builds a benchmark distribution: for each biomarker, the cohort
p10 / p25 / median / p75 / p90 and the cohort sample size, plus the patient's
own value placed against that distribution.

Selectable cohorts (config.COHORT_LABELS):
  - config.COHORT_NHANES ("nhanes_asian"): NHANES 2017-2018 Non-Hispanic Asian.
  - config.COHORT_SAHC   ("sahc"): South Asian Heart Center clinical cohort.
The default is config.DEFAULT_COHORT (NHANES), which preserves the original
single-cohort contract.

Data source resolution, per cohort:
  - If the cohort's real source files are present, percentiles are computed live.
  - Otherwise the cohort's frozen demo percentiles are used (the same real
    numbers). See demo_cohort.py / sahc_demo_cohort.py.

Output dicts are shaped exactly like api/models/results.py BenchmarkPoint:
    biomarker, patient_value, cohort_p10, cohort_p25, cohort_median,
    cohort_p75, cohort_p90, cohort_label, cohort_n

cohort_label always comes from config.cohort_label(cohort) — an honest,
cohort-specific label. The NHANES cohort is never labeled "South Asian".
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from sahc_risklens.clinical.biomarkers import get_biomarker_spec, get_field
from sahc_risklens.config import (
    COHORT_NHANES,
    COHORT_SAHC,
    DEFAULT_COHORT,
    cohort_label as _cohort_label,
)
from sahc_risklens.data.demo_cohort import get_demo_percentiles
from sahc_risklens.data.nhanes_loader import (
    BIOMARKER_KEYS,
    load_biomarker_frame,
    nhanes_files_available,
)
from sahc_risklens.data.sahc_cohort_loader import (
    load_biomarker_frame as load_sahc_biomarker_frame,
    load_matching_frame as load_sahc_matching_frame,
    sahc_file_available,
)
from sahc_risklens.data.sahc_demo_cohort import (
    get_demo_percentiles as get_sahc_demo_percentiles,
)
from sahc_risklens.data.strata_tables import get_strata_table
from sahc_risklens.benchmark.matching import (
    resolve_patient_strata,
    stratified_from_frame,
    stratified_from_table,
)

# Minimum non-missing cohort values for a biomarker to be benchmarked.
MIN_COHORT_N = 30

_PERCENTILE_POINTS = (10, 25, 50, 75, 90)

# Cohorts the benchmark layer knows how to build.
SUPPORTED_COHORTS = (COHORT_NHANES, COHORT_SAHC)


def _percentiles_from_frame(frame) -> dict[str, dict[str, float]]:
    """Compute p10/p25/median/p75/p90 + n per biomarker from a biomarker frame."""
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


def _validate_cohort(cohort: str) -> str:
    if cohort not in SUPPORTED_COHORTS:
        raise ValueError(
            f"Unknown cohort id: {cohort!r}. Supported: {SUPPORTED_COHORTS}"
        )
    return cohort


@lru_cache(maxsize=len(SUPPORTED_COHORTS))
def get_cohort_percentiles(cohort: str = DEFAULT_COHORT) -> dict[str, dict[str, float]]:
    """
    Return the percentile table for `cohort`, computed from real source files
    when available, otherwise the cohort's frozen demo table. Cached per cohort
    for the process lifetime (the underlying data does not change at runtime).
    """
    _validate_cohort(cohort)
    if cohort == COHORT_SAHC:
        if sahc_file_available():
            table = _percentiles_from_frame(load_sahc_biomarker_frame())
            if table:
                return table
        return get_sahc_demo_percentiles()

    # NHANES (default)
    if nhanes_files_available():
        table = _percentiles_from_frame(load_biomarker_frame())
        if table:
            return table
    return get_demo_percentiles()


def get_matched_percentiles(data, cohort: str = DEFAULT_COHORT) -> dict | None:
    """
    Peer-matched percentiles for `data` within `cohort`, or None when matching
    can't be applied (missing sex/age, no peer group reaches MIN_COHORT_N, or the
    cohort has no stratified source). Result shape (see matching.py):
        {"level", "description", "n", "per_biomarker": {key: {p10..p90, n}}}

    Source resolution mirrors get_cohort_percentiles: live matching frame when
    the raw cohort file is present, otherwise the frozen strata table.
    """
    _validate_cohort(cohort)
    strata = resolve_patient_strata(data)
    if not strata.can_match:
        return None

    if cohort == COHORT_SAHC:
        if sahc_file_available():
            return stratified_from_frame(load_sahc_matching_frame(), strata, BIOMARKER_KEYS)
        return stratified_from_table(get_strata_table(COHORT_SAHC), strata, BIOMARKER_KEYS)

    # NHANES: peer matching is not offered. The Non-Hispanic Asian cohort
    # (n ~= 382-1055 per biomarker) is too small to stratify by sex x age x
    # medication and stay above MIN_COHORT_N, and the raw files needed to do it
    # live are not shipped. match=True therefore falls back to the whole-cohort
    # distribution, disclosed at the call site (matched=False everywhere).
    return None


def get_benchmark_data(data, cohort: str = DEFAULT_COHORT, match: bool = False) -> list[dict]:
    """
    data: a BiomarkerInput instance or equivalent dict.
    cohort: which reference cohort to benchmark against (default NHANES).
    match: when True, benchmark each biomarker against the patient's matched peer
        subgroup (sex + age band + medication use), like the original SCORE tool —
        but with small-cell suppression and transparent fallback. A biomarker whose
        matched cell is too small falls back to the whole-cohort distribution and is
        flagged matched=False.

    Returns a list of BenchmarkPoint-shaped dicts, one per biomarker that has a
    cohort benchmark, in canonical biomarker order. Each point carries the
    reference distribution (so the frontend can always plot it) plus matching
    metadata: matched (bool), match_n (peer-group size or None), match_description
    (plain-language peer group, or None).
    """
    _validate_cohort(cohort)
    whole = get_cohort_percentiles(cohort)
    label = _cohort_label(cohort)
    matched = get_matched_percentiles(data, cohort) if match else None
    matched_per = matched["per_biomarker"] if matched else {}
    matched_desc = matched["description"] if matched else None

    points: list[dict] = []
    for key in BIOMARKER_KEYS:
        use_matched = key in matched_per
        stats = matched_per[key] if use_matched else whole.get(key)
        if stats is None:
            continue
        spec = get_biomarker_spec(key)
        points.append({
            "biomarker": key,
            "patient_value": get_field(data, spec.input_field),
            "cohort_p10": stats["p10"],
            "cohort_p25": stats["p25"],
            "cohort_median": stats["median"],
            "cohort_p75": stats["p75"],
            "cohort_p90": stats["p90"],
            "cohort_label": label,
            "cohort_n": int(stats["n"]),
            "matched": use_matched,
            "match_n": int(stats["n"]) if use_matched else None,
            "match_description": matched_desc if use_matched else None,
        })
    return points


def percentile_rank(value: float, key: str, cohort: str = DEFAULT_COHORT) -> float | None:
    """
    Approximate percentile rank (0-100) of `value` within the cohort, by linear
    interpolation across the stored p10/p25/median/p75/p90 anchors. Returns None
    if the biomarker has no benchmark. Intended for descriptive context only, not
    clinical classification (that is thresholds.py).
    """
    _validate_cohort(cohort)
    stats = get_cohort_percentiles(cohort).get(key)
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
    "SUPPORTED_COHORTS",
    "get_cohort_percentiles",
    "get_matched_percentiles",
    "get_benchmark_data",
    "percentile_rank",
]
