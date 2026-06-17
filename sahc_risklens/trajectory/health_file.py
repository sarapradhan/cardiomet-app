"""
sahc_risklens/trajectory/health_file.py

T0 — the user-owned, portable "health file": a plain dict (JSON-serializable)
that captures a BiomarkerSeries so the user can save it and re-import it later.
This is how longitudinal tracking works WITHOUT any server-side storage — the
patient owns the file. See docs/INCREMENTAL_VALUE_SPEC.md section 2.

Round-trip invariant: from_health_file(to_health_file(series)) == series
(dates serialize to ISO strings and parse back to date objects).
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from sahc_risklens.trajectory.series import (
    BiomarkerDraw,
    BiomarkerSeries,
    SeriesValidationError,
    make_series,
)

SCHEMA_VERSION = "1.0"
_SUPPORTED_SCHEMAS = {"1.0"}


class HealthFileError(ValueError):
    """Raised on a missing, unknown, or malformed health-file schema."""


def to_health_file(series: BiomarkerSeries) -> dict[str, Any]:
    """Serialize a series to a portable, JSON-ready dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "series": {
            "draws": [
                {
                    "draw_date": d.draw_date.isoformat(),
                    "values": dict(d.values),
                    "label": d.label,
                }
                for d in series.draws
            ]
        },
    }


def from_health_file(doc: dict[str, Any]) -> BiomarkerSeries:
    """
    Parse and validate a health-file dict back into a BiomarkerSeries.
    Raises HealthFileError on a missing/unknown schema or malformed structure.
    """
    if not isinstance(doc, dict) or "schema_version" not in doc:
        raise HealthFileError("Missing schema_version.")
    if doc["schema_version"] not in _SUPPORTED_SCHEMAS:
        raise HealthFileError(f"Unsupported schema_version: {doc['schema_version']!r}")

    try:
        raw_draws = doc["series"]["draws"]
    except (KeyError, TypeError) as exc:
        raise HealthFileError("Malformed health file: missing series.draws.") from exc

    draws: list[BiomarkerDraw] = []
    for raw in raw_draws:
        try:
            draw_date = dt.date.fromisoformat(raw["draw_date"])
        except (KeyError, TypeError, ValueError) as exc:
            raise HealthFileError(f"Malformed draw_date in: {raw!r}") from exc
        draws.append(BiomarkerDraw(
            draw_date=draw_date,
            values=dict(raw.get("values", {})),
            label=raw.get("label"),
        ))

    try:
        return make_series(draws)
    except SeriesValidationError as exc:
        raise HealthFileError(str(exc)) from exc


__all__ = ["SCHEMA_VERSION", "HealthFileError", "to_health_file", "from_health_file"]
