"""
scripts/build_strata_tables.py

Regenerate sahc_risklens/data/strata_tables.json — the frozen, aggregate-only
stratified percentile tables used for peer matching in demo mode.

Run from the repo root with the SAHC cohort CSV present at data/sahc/:
    python scripts/build_strata_tables.py

Only aggregates (per-stratum percentiles + counts) are written. Cells below
MIN_MATCH_N people, and biomarkers below MIN_MATCH_N values, are suppressed.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

from sahc_risklens.benchmark.matching import AGE_BAND_LABELS, MIN_MATCH_N, stratum_key
from sahc_risklens.config import COHORT_SAHC
from sahc_risklens.data.sahc_cohort_loader import (
    BIOMARKER_KEYS,
    load_matching_frame,
    sahc_file_available,
)

OUT = Path("sahc_risklens/data/strata_tables.json")


def _pct(series):
    arr = series.dropna().to_numpy()
    if len(arr) < MIN_MATCH_N:
        return None
    p10, p25, p50, p75, p90 = np.percentile(arr, (10, 25, 50, 75, 90))
    return {"p10": round(float(p10), 1), "p25": round(float(p25), 1),
            "median": round(float(p50), 1), "p75": round(float(p75), 1),
            "p90": round(float(p90), 1), "n": int(len(arr))}


def _add(table, frame, mask, key):
    sub = frame[mask]
    if len(sub) < MIN_MATCH_N:
        return
    entry = {"_n": int(len(sub))}
    for k in BIOMARKER_KEYS:
        stats = _pct(sub[k])
        if stats:
            entry[k] = stats
    if len(entry) > 1:
        table[key] = entry


def build_sahc() -> dict:
    frame = load_matching_frame()
    table: dict = {}
    sexes, bands = ["M", "F"], list(AGE_BAND_LABELS.keys())
    for s, b in itertools.product(sexes, bands):
        _add(table, frame, (frame.sex == s) & (frame.age_band == b), stratum_key(s, b))
    for s, b in itertools.product(sexes, bands):
        for c, bp, d in itertools.product([False, True], repeat=3):
            _add(table, frame,
                 (frame.sex == s) & (frame.age_band == b)
                 & (frame.chol_med == c) & (frame.bp_med == bp) & (frame.dm_med == d),
                 stratum_key(s, b, c, bp, d))
    return table


def main() -> None:
    if not sahc_file_available():
        raise SystemExit("SAHC cohort CSV not found at data/sahc/ — cannot regenerate.")
    tables = {COHORT_SAHC: build_sahc()}
    OUT.write_text(json.dumps(tables, indent=0))
    print(f"Wrote {OUT} with {len(tables[COHORT_SAHC])} {COHORT_SAHC} strata.")


if __name__ == "__main__":
    main()
