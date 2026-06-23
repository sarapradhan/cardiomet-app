"""
sahc_risklens/benchmark/matching.py

Peer matching for the benchmark — the capability the original SCORE tool had:
compare a patient against a reference subgroup matched on sex, age band, and
medication use, rather than against the whole cohort.

How this IMPROVES on SCORE: SCORE computed a percentile on whatever matched cell
resulted, however small. Here we suppress cells below MIN_MATCH_N (statistically
unreliable peer groups), fall back transparently to a broader group, and always
report the matched n and a plain-language description of the peer group actually
used. So matching is applied when it is reliable and disclosed when it is not.

Matching dimensions (mirror SCORE's `ui_choose`):
  - sex      : "M" / "F"
  - age_band : 5 bands by lower bound — 19 (18-33), 34 (34-48), 49 (49-64),
               65 (65-78), 79 (79+)
  - meds     : cholesterol / blood-pressure / diabetes medication use

Match levels, narrowest first:
  1. "full"    — sex + age band + all three medication flags
  2. "sexage"  — sex + age band
  3. "cohort"  — the whole cohort (no matching; matched=False)
We use the narrowest level whose peer group has at least MIN_MATCH_N people;
within that level, any individual biomarker with fewer than MIN_MATCH_N values
falls back to the whole-cohort distribution for that biomarker (flagged).

This module holds pure, pandas-free helpers plus the stratified-percentile
computation; the data source (live frame vs frozen strata table) is resolved by
percentile.py.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Minimum people in a peer group (and minimum values per biomarker) for a
# matched percentile to be shown. Kept equal to the whole-cohort floor.
MIN_MATCH_N = 30

# Age bands by inclusive lower bound -> display label.
AGE_BAND_LABELS: dict[int, str] = {
    19: "18–33",
    34: "34–48",
    49: "49–64",
    65: "65–78",
    79: "79+",
}
_AGE_BAND_BOUNDS = [(34, 19), (49, 34), (65, 49), (79, 65)]  # (upper_exclusive, code)


def age_to_band(age) -> int | None:
    """Map an age in years to its band code (lower bound). None if age is missing."""
    try:
        a = float(age)
    except (TypeError, ValueError):
        return None
    if a != a:  # NaN
        return None
    if a < 19:
        # Under 19: the cohort's adult bands don't apply; treat as unmatched.
        # (Patient input is constrained to >= 18; an 18yo is grouped with 18-33.)
        return 19 if a >= 18 else None
    for upper, code in _AGE_BAND_BOUNDS:
        if a < upper:
            return code
    return 79


@dataclass(frozen=True)
class PatientStrata:
    """A patient's matching attributes, normalized."""
    sex: str | None          # "M" / "F" / None
    age_band: int | None     # band code / None
    chol_med: bool
    bp_med: bool
    dm_med: bool

    @property
    def can_match(self) -> bool:
        """Matching requires at least sex and age band to be known."""
        return self.sex is not None and self.age_band is not None


def resolve_patient_strata(data) -> PatientStrata:
    """Build PatientStrata from a BiomarkerInput-like object or dict."""
    from sahc_risklens.clinical.biomarkers import get_field

    sex = get_field(data, "sex")
    sex = sex if sex in ("M", "F") else None
    return PatientStrata(
        sex=sex,
        age_band=age_to_band(get_field(data, "age_yr")),
        chol_med=bool(get_field(data, "chol_med")),
        bp_med=bool(get_field(data, "bp_med")),
        # Either diabetes-pill or insulin use counts as diabetes medication.
        dm_med=bool(get_field(data, "dm_pills")) or bool(get_field(data, "insulin")),
    )


def stratum_key(sex, age_band, chol=None, bp=None, dm=None) -> str:
    """
    Canonical key for a stratum. None -> '*' (wildcard). Used for the frozen
    strata table and for describing the level.
    """
    def t(v):
        if v is None:
            return "*"
        if isinstance(v, bool):
            return "1" if v else "0"
        return str(v)
    return f"sex={t(sex)}|age={t(age_band)}|chol={t(chol)}|bp={t(bp)}|dm={t(dm)}"


def describe_strata(strata: PatientStrata, level: str) -> str:
    """Plain-language description of the matched peer group at a given level."""
    if level == "cohort" or strata.sex is None or strata.age_band is None:
        return "full cohort"
    sex_word = "Men" if strata.sex == "M" else "Women"
    parts = [f"{sex_word}, {AGE_BAND_LABELS.get(strata.age_band, strata.age_band)}"]
    if level == "full":
        meds = []
        if strata.chol_med:
            meds.append("cholesterol")
        if strata.bp_med:
            meds.append("blood-pressure")
        if strata.dm_med:
            meds.append("diabetes")
        if meds:
            parts.append("on " + ", ".join(meds) + " medication")
        else:
            parts.append("not on lipid/BP/diabetes medication")
    return ", ".join(parts)


def percentiles_from_series(values) -> dict[str, float] | None:
    """p10/p25/median/p75/p90 + n from a 1-D array-like; None if < MIN_MATCH_N."""
    arr = np.asarray([v for v in values if v == v], dtype=float)  # drop NaN
    if len(arr) < MIN_MATCH_N:
        return None
    p10, p25, p50, p75, p90 = np.percentile(arr, (10, 25, 50, 75, 90))
    return {
        "p10": round(float(p10), 1), "p25": round(float(p25), 1),
        "median": round(float(p50), 1), "p75": round(float(p75), 1),
        "p90": round(float(p90), 1), "n": int(len(arr)),
    }


# Ordered match levels, narrowest first. Each is a predicate over a strata.
MATCH_LEVELS = ("full", "sexage")


def _frame_mask(frame, strata: PatientStrata, level: str):
    """Boolean mask selecting the rows of `frame` in the given match level."""
    mask = (frame["sex"] == strata.sex) & (frame["age_band"] == strata.age_band)
    if level == "full":
        mask = mask & (frame["chol_med"] == strata.chol_med) \
                    & (frame["bp_med"] == strata.bp_med) \
                    & (frame["dm_med"] == strata.dm_med)
    return mask


def stratified_from_frame(frame, strata: PatientStrata, biomarker_keys) -> dict | None:
    """
    Compute a matched peer benchmark from a live matching-frame.

    Returns None if the patient can't be matched (missing sex/age) or no level
    reaches MIN_MATCH_N. Otherwise:
        {
          "level": "full" | "sexage",
          "description": str,
          "n": int,                      # people in the peer group
          "per_biomarker": {key: {p10..p90, n}}  # only biomarkers >= MIN_MATCH_N
        }
    """
    if not strata.can_match:
        return None
    for level in MATCH_LEVELS:
        mask = _frame_mask(frame, strata, level)
        n = int(mask.sum())
        if n < MIN_MATCH_N:
            continue
        sub = frame[mask]
        per: dict[str, dict] = {}
        for key in biomarker_keys:
            if key in sub.columns:
                stats = percentiles_from_series(sub[key].to_numpy())
                if stats is not None:
                    per[key] = stats
        if per:
            return {"level": level, "description": describe_strata(strata, level),
                    "n": n, "per_biomarker": per}
    return None


def stratified_from_table(table: dict, strata: PatientStrata, biomarker_keys) -> dict | None:
    """
    Same contract as stratified_from_frame, but sourced from a frozen strata
    table (see data/strata_tables.py). `table` maps stratum_key -> entry, where
    each entry is {"_n": people, "<biomarker>": {p10..p90, n}, ...}.
    """
    if not strata.can_match:
        return None
    keys_by_level = {
        "full": stratum_key(strata.sex, strata.age_band,
                            strata.chol_med, strata.bp_med, strata.dm_med),
        "sexage": stratum_key(strata.sex, strata.age_band),
    }
    for level in MATCH_LEVELS:
        entry = table.get(keys_by_level[level])
        if not entry or int(entry.get("_n", 0)) < MIN_MATCH_N:
            continue
        per = {k: entry[k] for k in biomarker_keys
               if k in entry and isinstance(entry[k], dict) and entry[k].get("n", 0) >= MIN_MATCH_N}
        if per:
            return {"level": level, "description": describe_strata(strata, level),
                    "n": int(entry["_n"]), "per_biomarker": per}
    return None


__all__ = [
    "MIN_MATCH_N",
    "AGE_BAND_LABELS",
    "age_to_band",
    "PatientStrata",
    "resolve_patient_strata",
    "stratum_key",
    "describe_strata",
    "percentiles_from_series",
    "stratified_from_frame",
    "stratified_from_table",
]
