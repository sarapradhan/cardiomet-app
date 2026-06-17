"""
sahc_risklens/trajectory/series.py

T0 — the dated-draw and series data model. Framework-free dataclasses plus a
validating constructor. See docs/trajectory/DESIGN_TRAJECTORY_T0_T1.md.

A draw is one dated lab panel (the existing 16-field input, held as a plain
dict so the clinical core stays independent of the API's Pydantic models). A
series is an immutable, date-sorted set of draws.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any, Iterable


class SeriesValidationError(ValueError):
    """Raised when a series is empty or contains a future-dated draw."""


@dataclass(frozen=True)
class BiomarkerDraw:
    """One dated lab panel. `values` holds the existing input fields by name."""
    draw_date: dt.date
    values: dict[str, Any] = field(default_factory=dict)
    label: str | None = None


@dataclass(frozen=True)
class BiomarkerSeries:
    """An immutable, ascending-by-date set of draws for one person."""
    draws: tuple[BiomarkerDraw, ...]


def make_series(draws: Iterable[BiomarkerDraw]) -> BiomarkerSeries:
    """
    Validate and normalize an iterable of draws into a BiomarkerSeries:
      - reject an empty series
      - reject any draw dated in the future
      - sort ascending by draw_date (stable)

    Future dates are rejected because a lab draw cannot postdate today, and
    forbidding them also keeps the engine honest: it only ever describes the
    past (see the descriptive-only safety requirement).
    """
    draws = list(draws)
    if not draws:
        raise SeriesValidationError("A series must contain at least one draw.")

    today = dt.date.today()
    for d in draws:
        if d.draw_date > today:
            raise SeriesValidationError(
                f"Draw date {d.draw_date.isoformat()} is in the future."
            )

    ordered = tuple(sorted(draws, key=lambda d: d.draw_date))
    return BiomarkerSeries(draws=ordered)


__all__ = [
    "BiomarkerDraw",
    "BiomarkerSeries",
    "SeriesValidationError",
    "make_series",
]
