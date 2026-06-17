"""
tests/test_series.py

T0 tests — written before implementation (TDD). Covers the dated-draw and series
data model and the portable health-file round-trip. See
docs/trajectory/DESIGN_TRAJECTORY_T0_T1.md.
"""
from __future__ import annotations

import datetime as dt

import pytest

from sahc_risklens.trajectory.series import (
    BiomarkerDraw,
    BiomarkerSeries,
    SeriesValidationError,
    make_series,
)
from sahc_risklens.trajectory.health_file import (
    SCHEMA_VERSION,
    HealthFileError,
    from_health_file,
    to_health_file,
)


def _draw(date_str: str, **values) -> BiomarkerDraw:
    base = {
        "LDL_mgdl": 100, "HDL_mgdl": 55, "TG_mgdl": 120, "TC_mgdl": 180,
        "FPG_mgdl": 95, "HbA1c_pct": 5.4, "SBP_mmhg": 118, "DBP_mmhg": 76,
        "BMI_kgm2": 24.0, "age_yr": 45, "sex": "M", "south_asian": True,
        "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
    }
    base.update(values)
    return BiomarkerDraw(draw_date=dt.date.fromisoformat(date_str), values=base)


# --------------------------------------------------------------------------
# Construction & validation
# --------------------------------------------------------------------------

def test_make_series_sorts_ascending_by_date():
    s = make_series([_draw("2026-05-01"), _draw("2025-12-01"), _draw("2026-01-15")])
    dates = [d.draw_date.isoformat() for d in s.draws]
    assert dates == ["2025-12-01", "2026-01-15", "2026-05-01"]


def test_make_series_rejects_empty():
    with pytest.raises(SeriesValidationError):
        make_series([])


def test_make_series_rejects_future_date():
    future = (dt.date.today() + dt.timedelta(days=2)).isoformat()
    with pytest.raises(SeriesValidationError):
        make_series([_draw(future)])


def test_series_is_immutable():
    s = make_series([_draw("2025-12-01")])
    assert isinstance(s.draws, tuple)
    with pytest.raises((AttributeError, TypeError)):
        s.draws = ()  # type: ignore[misc]


def test_draw_carries_optional_label():
    d = BiomarkerDraw(draw_date=dt.date(2026, 1, 1), values={}, label="after statin")
    assert d.label == "after statin"


def test_single_draw_series_is_valid():
    s = make_series([_draw("2026-01-01")])
    assert len(s.draws) == 1


# --------------------------------------------------------------------------
# Health file round-trip
# --------------------------------------------------------------------------

def test_health_file_has_schema_and_series():
    s = make_series([_draw("2025-12-01"), _draw("2026-05-01")])
    doc = to_health_file(s)
    assert doc["schema_version"] == SCHEMA_VERSION
    assert "exported_at" in doc
    assert len(doc["series"]["draws"]) == 2


def test_health_file_round_trip_lossless():
    s = make_series([
        _draw("2025-12-01", LDL_mgdl=162, chol_med=False),
        _draw("2026-05-01", LDL_mgdl=124, chol_med=True),
    ])
    restored = from_health_file(to_health_file(s))
    assert [d.draw_date for d in restored.draws] == [d.draw_date for d in s.draws]
    assert restored.draws[0].values["LDL_mgdl"] == 162
    assert restored.draws[1].values["chol_med"] is True


def test_health_file_dates_are_iso_strings_in_doc():
    doc = to_health_file(make_series([_draw("2026-01-15")]))
    assert doc["series"]["draws"][0]["draw_date"] == "2026-01-15"


def test_from_health_file_rejects_unknown_schema():
    doc = to_health_file(make_series([_draw("2026-01-01")]))
    doc["schema_version"] = "99.0"
    with pytest.raises(HealthFileError):
        from_health_file(doc)


def test_from_health_file_rejects_missing_schema():
    with pytest.raises(HealthFileError):
        from_health_file({"series": {"draws": []}})


def test_from_health_file_preserves_label():
    s = BiomarkerSeries(draws=(BiomarkerDraw(dt.date(2026, 1, 1), {"LDL_mgdl": 100}, "baseline"),))
    restored = from_health_file(to_health_file(s))
    assert restored.draws[0].label == "baseline"
