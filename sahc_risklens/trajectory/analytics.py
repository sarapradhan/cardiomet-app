"""
sahc_risklens/trajectory/analytics.py

T1 — descriptive trajectory analytics. Turns a BiomarkerSeries into per-biomarker
trajectories (direction, change, rate, category transitions) and intervention
markers. See docs/trajectory/DESIGN_TRAJECTORY_T0_T1.md.

Design commitments:
  - Reuses the clinical core for every clinical judgment: per-point categories
    come from clinical.thresholds.classify_all_biomarkers; the medication map
    comes from clinical.thresholds.medication_affects(). No new thresholds.
  - Descriptive only. Nothing here projects a future value, attributes cause to
    an intervention, or emits a risk score. "worsening" describes a number's
    movement relative to the guideline-preferred direction, not a person.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from sahc_risklens.clinical.biomarkers import BIOMARKERS, get_biomarker_spec
from sahc_risklens.clinical.disclaimers import medication_labels
from sahc_risklens.clinical.thresholds import (
    classify_all_biomarkers,
    medication_affects,
)
from sahc_risklens.trajectory.series import BiomarkerSeries

# The only biomarker for which a higher value is the guideline-preferred direction.
HIGHER_IS_BETTER: frozenset[str] = frozenset({"HDL"})

# Per-biomarker display-noise deadband: a change smaller than this reads as
# "stable" rather than improving/worsening. This is a presentation threshold to
# avoid over-reading lab noise, NOT a statement of clinical significance.
_DEADBAND: dict[str, float] = {
    "LDL": 5, "HDL": 3, "TG": 10, "TC": 5, "HbA1c": 0.1,
    "FPG": 3, "SBP": 3, "DBP": 3, "BMI": 0.3,
}

# Tone grouping — server-side mirror of the frontend categoryStyles grouping.
# (The frontend cannot import Python; a test asserts every category the
# classifier can emit maps to a known tone, preventing drift.)
_HIGH_TONE = frozenset({
    "High", "Very High", "Diabetes", "Stage 2 Hypertension", "High risk", "Obese",
})
_ELEVATED_TONE = frozenset({
    "Near Optimal", "Borderline High", "Prediabetes", "Elevated",
    "Stage 1 Hypertension", "Increased risk", "Overweight", "Underweight", "Low",
})
_NORMAL_TONE = frozenset({"Optimal", "Normal", "Desirable", "Protective"})


def _tone(category: str | None) -> str:
    if category is None:
        return "missing"
    if category in _HIGH_TONE:
        return "high"
    if category in _ELEVATED_TONE:
        return "elevated"
    if category in _NORMAL_TONE:
        return "normal"
    return "elevated"  # present but unrecognized: surface it, never hide it


# --------------------------------------------------------------------------
# Dataclasses
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class TrajectoryPoint:
    draw_date: dt.date
    value: float | None
    category: str | None
    category_tone: str


@dataclass(frozen=True)
class CategoryTransition:
    from_category: str
    to_category: str
    from_date: dt.date
    to_date: dt.date


@dataclass(frozen=True)
class BiomarkerTrajectory:
    biomarker: str
    unit: str
    points: tuple[TrajectoryPoint, ...]
    direction: str
    change_absolute: float | None
    change_per_year: float | None
    transitions: tuple[CategoryTransition, ...]
    n_points: int


@dataclass(frozen=True)
class InterventionMarker:
    draw_date: dt.date
    change: str
    affected_biomarkers: tuple[str, ...]
    observed_effects: tuple[str, ...]


@dataclass(frozen=True)
class SeriesAnalysis:
    trajectories: tuple[BiomarkerTrajectory, ...]
    interventions: tuple[InterventionMarker, ...]


# --------------------------------------------------------------------------
# Per-biomarker computation
# --------------------------------------------------------------------------

def _direction(label: str, present: list[tuple[dt.date, float]]) -> str:
    if len(present) < 2:
        return "insufficient_data"
    delta = present[-1][1] - present[0][1]
    if abs(delta) < _DEADBAND.get(label, 0):
        return "stable"
    good = delta if label in HIGHER_IS_BETTER else -delta
    return "improving" if good > 0 else "worsening"


def _rate_per_year(present: list[tuple[dt.date, float]]) -> float | None:
    if len(present) < 2:
        return None
    t0 = present[0][0]
    xs = [(d - t0).days / 365.25 for d, _ in present]
    ys = [v for _, v in present]
    span = xs[-1] - xs[0]
    if span <= 0:
        return None
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return round(num / den, 2)


def _categories_per_draw(series: BiomarkerSeries) -> list[dict[str, str | None]]:
    """For each draw, map biomarker label -> category via the clinical core."""
    out: list[dict[str, str | None]] = []
    for draw in series.draws:
        results = classify_all_biomarkers(draw.values)
        out.append({r["biomarker"]: r["category"] for r in results})
    return out


def _transitions(series: BiomarkerSeries, label: str,
                 per_draw: list[dict[str, str | None]]) -> tuple[CategoryTransition, ...]:
    transitions: list[CategoryTransition] = []
    for i in range(1, len(series.draws)):
        prev_cat = per_draw[i - 1].get(label)
        cur_cat = per_draw[i].get(label)
        if prev_cat is not None and cur_cat is not None and prev_cat != cur_cat:
            transitions.append(CategoryTransition(
                from_category=prev_cat, to_category=cur_cat,
                from_date=series.draws[i - 1].draw_date,
                to_date=series.draws[i].draw_date,
            ))
    return tuple(transitions)


def _trajectory(series: BiomarkerSeries, label: str,
                per_draw: list[dict[str, str | None]]) -> BiomarkerTrajectory:
    spec = get_biomarker_spec(label)
    points: list[TrajectoryPoint] = []
    present: list[tuple[dt.date, float]] = []

    for i, draw in enumerate(series.draws):
        raw = draw.values.get(spec.input_field)
        value = float(raw) if isinstance(raw, (int, float)) else None
        category = per_draw[i].get(label)
        points.append(TrajectoryPoint(
            draw_date=draw.draw_date, value=value,
            category=category, category_tone=_tone(category),
        ))
        if value is not None:
            present.append((draw.draw_date, value))

    change_absolute = round(present[-1][1] - present[0][1], 2) if len(present) >= 2 else None

    return BiomarkerTrajectory(
        biomarker=label,
        unit=spec.unit,
        points=tuple(points),
        direction=_direction(label, present),
        change_absolute=change_absolute,
        change_per_year=_rate_per_year(present),
        transitions=_transitions(series, label, per_draw),
        n_points=len(present),
    )


# --------------------------------------------------------------------------
# Interventions
# --------------------------------------------------------------------------

def _describe_effect(label: str, unit: str, before: float, after: float) -> str:
    diff = round(after - before, 2)
    if diff == 0:
        movement = "no change"
    else:
        movement = f"{'decreased' if diff < 0 else 'increased'} {abs(diff)} {unit}"
    # Strictly observational phrasing: states what changed, not why.
    return f"{label} changed from {before} to {after} ({movement}) by the next draw"


def _interventions(series: BiomarkerSeries) -> tuple[InterventionMarker, ...]:
    affects = medication_affects()
    labels = medication_labels()
    markers: list[InterventionMarker] = []

    for i in range(1, len(series.draws)):
        prev, cur = series.draws[i - 1], series.draws[i]
        for flag, affected in affects.items():
            if (not prev.values.get(flag)) and cur.values.get(flag):
                effects: list[str] = []
                for bm in BIOMARKERS:
                    if bm.label not in affected:
                        continue
                    a = prev.values.get(bm.input_field)
                    b = cur.values.get(bm.input_field)
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        effects.append(_describe_effect(bm.label, bm.unit, float(a), float(b)))
                markers.append(InterventionMarker(
                    draw_date=cur.draw_date,
                    change=f"started {labels.get(flag, flag)}",
                    affected_biomarkers=tuple(sorted(affected)),
                    observed_effects=tuple(effects),
                ))
    return tuple(markers)


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------

def analyze_series(series: BiomarkerSeries) -> SeriesAnalysis:
    """
    Compute descriptive trajectories for all nine biomarkers plus intervention
    markers. Reuses the clinical core for categories and the medication map;
    introduces no clinical thresholds; emits no predictive or causal language.
    """
    per_draw = _categories_per_draw(series)
    trajectories = tuple(
        _trajectory(series, spec.label, per_draw) for spec in BIOMARKERS
    )
    return SeriesAnalysis(trajectories=trajectories, interventions=_interventions(series))


__all__ = [
    "HIGHER_IS_BETTER",
    "TrajectoryPoint",
    "CategoryTransition",
    "BiomarkerTrajectory",
    "InterventionMarker",
    "SeriesAnalysis",
    "analyze_series",
]
