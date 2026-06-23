"""
sahc_risklens/data/strata_tables.py

Frozen, aggregate-only stratified percentile tables for peer matching, used when
the raw cohort file is not present (the default deployment). Mirrors how
demo_cohort.py relates to the live loader: the numbers here are the REAL matched
percentiles computed once from the cohort and frozen for reproducibility.

Contents are aggregates ONLY — per-stratum percentiles and counts. No patient
rows. Cells below MIN_MATCH_N people, and individual biomarkers below MIN_MATCH_N
values, are suppressed at generation time (so absence == "too small to report").

Regenerate with scripts/build_strata_tables.py when the cohort data changes.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_TABLE_PATH = Path(__file__).with_name("strata_tables.json")


@lru_cache(maxsize=1)
def _all_tables() -> dict:
    if not _TABLE_PATH.exists():
        return {}
    return json.loads(_TABLE_PATH.read_text())


def get_strata_table(cohort: str) -> dict:
    """Frozen stratum_key -> entry map for a cohort ({} if none frozen)."""
    return _all_tables().get(cohort, {})


__all__ = ["get_strata_table"]
