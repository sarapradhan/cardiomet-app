"""
sahc_risklens/data/strata_tables.py

Reader for frozen, aggregate-only stratified percentile tables used by peer
matching. Tables are keyed by cohort id.

NO TABLE SHIPS TODAY. strata_tables.json was removed on 2026-08-30 along with the
"sahc" cohort, whose provenance could not be established (docs/SAHC_COHORT.md).
This reader is retained deliberately: it is the seam a properly sourced cohort
plugs into, and get_strata_table() already returns {} when no table is present,
so peer matching degrades to the whole-cohort distribution with matched=False.

The contract for any future table: aggregates ONLY — per-stratum percentiles and
counts, never patient rows — with cells below MIN_MATCH_N people, and individual
biomarkers below MIN_MATCH_N values, suppressed at generation time (so absence
means "too small to report").
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
