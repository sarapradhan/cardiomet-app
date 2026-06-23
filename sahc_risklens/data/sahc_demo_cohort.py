"""
sahc_risklens/data/sahc_demo_cohort.py

Frozen aggregate percentiles for the South Asian Heart Center (SAHC) clinical
cohort, used when the raw patient CSV is not present (the default deployment —
the raw rows are never committed; see docs/SAHC_COHORT.md and .gitignore).

These are the REAL SAHC cohort percentiles (South Asian patients, RIDRETH3 == 1),
computed once from data/sahc/sahc_cohort_noPID.csv and frozen here so the demo
deployment reports true-to-source numbers with zero runtime data dependency and
perfect reproducibility. When the raw CSV IS present,
sahc_risklens/benchmark/percentile.py recomputes from it via sahc_cohort_loader
and ignores this module. Keeping the frozen numbers identical to the live
computation means switching between demo and live mode does not change the
displayed benchmark.

cohort_label for this data is always config.SAHC_COHORT_LABEL
("South Asian Heart Center clinical cohort"). It is NEVER labeled with the NHANES
cohort string.

Caveats baked into these numbers (see sahc_cohort_loader docstring):
  - FPG includes non-fasting draws (no fasting-hours field in the source).
  - SBP/DBP are single oscillometric readings, not three-reading means.
"""
from __future__ import annotations

# Frozen real SAHC South Asian cohort percentiles. Each entry:
#   {p10, p25, median, p75, p90, n}
# Source: data/sahc/sahc_cohort_noPID.csv, RIDRETH3 == 1, computed 2026-06-22.
_DEMO_PERCENTILES: dict[str, dict[str, float]] = {
    "LDL":   {"p10": 73.0,  "p25": 91.0,  "median": 112.0, "p75": 135.0, "p90": 156.0, "n": 9704},
    "HDL":   {"p10": 33.0,  "p25": 38.0,  "median": 45.0,  "p75": 54.0,  "p90": 64.0,  "n": 9754},
    "TG":    {"p10": 63.0,  "p25": 84.0,  "median": 118.0, "p75": 166.0, "p90": 225.0, "n": 9750},
    "TC":    {"p10": 141.0, "p25": 162.0, "median": 186.0, "p75": 212.0, "p90": 236.0, "n": 9754},
    "HbA1c": {"p10": 5.2,   "p25": 5.4,   "median": 5.6,   "p75": 6.0,   "p90": 6.5,   "n": 6046},
    "FPG":   {"p10": 83.0,  "p25": 87.0,  "median": 93.0,  "p75": 101.0, "p90": 117.0, "n": 4497},
    "SBP":   {"p10": 100.0, "p25": 108.0, "median": 118.0, "p75": 130.0, "p90": 142.0, "n": 8796},
    "DBP":   {"p10": 61.0,  "p25": 68.0,  "median": 75.0,  "p75": 82.0,  "p90": 89.0,  "n": 8796},
    "BMI":   {"p10": 21.3,  "p25": 23.1,  "median": 25.2,  "p75": 27.8,  "p90": 30.7,  "n": 8808},
}


def get_demo_percentiles() -> dict[str, dict[str, float]]:
    """Return a deep copy of the frozen SAHC percentile table (safe to mutate)."""
    return {key: dict(stats) for key, stats in _DEMO_PERCENTILES.items()}


def demo_biomarker_keys() -> list[str]:
    """Internal biomarker keys covered by the SAHC demo benchmark."""
    return list(_DEMO_PERCENTILES.keys())


__all__ = ["get_demo_percentiles", "demo_biomarker_keys"]
