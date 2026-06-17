"""
sahc_risklens/data/demo_cohort.py

Deterministic demo benchmark for the stateless Phase 1 deployment, where the
raw NHANES XPT files are not shipped.

These percentile values are the REAL NHANES 2017-2018 Non-Hispanic Asian cohort
percentiles (RIDRETH3 == 6), computed once from the public data files and frozen
here so the demo deployment reports true-to-source numbers with zero runtime
data dependency and perfect reproducibility. Fasting plasma glucose (FPG) uses
only fasting participants (PHAFSTHR >= 8), and SBP/DBP use the mean of the three
readings, exactly as the live loader computes them.

When the real XPT files ARE present, sahc_risklens/benchmark/percentile.py
recomputes percentiles from them via nhanes_loader and ignores this module.
Keeping the demo numbers identical to the real computation means switching
between demo and live mode does not change the displayed benchmark.

cohort_label for this data is always config.NHANES_COHORT_LABEL
("NHANES Non-Hispanic Asian").
"""
from __future__ import annotations

# Frozen real NH-Asian percentiles. Each entry:
#   {p10, p25, median, p75, p90, n}
# Source: NHANES 2017-2018 public files, RIDRETH3 == 6, computed 2026-06-13.
_DEMO_PERCENTILES: dict[str, dict[str, float]] = {
    "LDL":   {"p10": 69.0,  "p25": 84.2,  "median": 106.0, "p75": 132.0, "p90": 160.0, "n": 382},
    "HDL":   {"p10": 38.0,  "p25": 44.0,  "median": 52.0,  "p75": 62.0,  "p90": 72.0,  "n": 892},
    "TG":    {"p10": 42.4,  "p25": 60.0,  "median": 91.0,  "p75": 136.0, "p90": 202.0, "n": 385},
    "TC":    {"p10": 137.0, "p25": 159.0, "median": 182.0, "p75": 212.0, "p90": 240.0, "n": 892},
    "HbA1c": {"p10": 5.1,   "p25": 5.3,   "median": 5.6,   "p75": 6.0,   "p90": 6.8,   "n": 836},
    "FPG":   {"p10": 91.0,  "p25": 96.2,  "median": 103.0, "p75": 115.0, "p90": 136.2, "n": 378},
    "SBP":   {"p10": 100.0, "p25": 107.3, "median": 117.3, "p75": 130.7, "p90": 146.0, "n": 891},
    "DBP":   {"p10": 54.0,  "p25": 63.3,  "median": 72.0,  "p75": 78.7,  "p90": 86.0,  "n": 891},
    "BMI":   {"p10": 16.1,  "p25": 20.4,  "median": 24.0,  "p75": 27.5,  "p90": 31.3,  "n": 1055},
}


def get_demo_percentiles() -> dict[str, dict[str, float]]:
    """Return a deep copy of the frozen demo percentile table (safe to mutate)."""
    return {key: dict(stats) for key, stats in _DEMO_PERCENTILES.items()}


def demo_biomarker_keys() -> list[str]:
    """Internal biomarker keys covered by the demo benchmark."""
    return list(_DEMO_PERCENTILES.keys())


__all__ = ["get_demo_percentiles", "demo_biomarker_keys"]
