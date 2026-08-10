"""
tests/test_trajectory_analytics.py

T1 tests — written before implementation (TDD). Covers descriptive trajectory
analytics and the descriptive-only safety guardrails. Expected values are
hand-computed. See docs/trajectory/DESIGN_TRAJECTORY_T0_T1.md.
"""
from __future__ import annotations

import datetime as dt

from sahc_risklens.trajectory.analytics import (
    SeriesAnalysis,
    analyze_series,
)
from sahc_risklens.trajectory.series import BiomarkerDraw, make_series

_BASE = {
    "LDL_mgdl": 100, "HDL_mgdl": 55, "TG_mgdl": 120, "TC_mgdl": 180,
    "FPG_mgdl": 95, "HbA1c_pct": 5.4, "SBP_mmhg": 118, "DBP_mmhg": 76,
    "BMI_kgm2": 24.0, "age_yr": 45, "sex": "M", "south_asian": True,
    "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
}


def _draw(date_str: str, **overrides) -> BiomarkerDraw:
    v = {**_BASE, **overrides}
    return BiomarkerDraw(draw_date=dt.date.fromisoformat(date_str), values=v)


def _traj(analysis: SeriesAnalysis, biomarker: str):
    return next(t for t in analysis.trajectories if t.biomarker == biomarker)


# --------------------------------------------------------------------------
# Direction
# --------------------------------------------------------------------------

def test_ldl_decreasing_is_improving():
    """LDL is lower-is-better: 162 -> 124 is improving."""
    a = analyze_series(make_series([_draw("2025-12-01", LDL_mgdl=162),
                                    _draw("2026-05-01", LDL_mgdl=124)]))
    assert _traj(a, "LDL").direction == "improving"


def test_ldl_increasing_is_worsening():
    a = analyze_series(make_series([_draw("2025-12-01", LDL_mgdl=100),
                                    _draw("2026-05-01", LDL_mgdl=150)]))
    assert _traj(a, "LDL").direction == "worsening"


def test_hdl_increasing_is_improving():
    """HDL is the one higher-is-better biomarker: 40 -> 60 is improving."""
    a = analyze_series(make_series([_draw("2025-12-01", HDL_mgdl=40),
                                    _draw("2026-05-01", HDL_mgdl=60)]))
    assert _traj(a, "HDL").direction == "improving"


def test_hdl_decreasing_is_worsening():
    a = analyze_series(make_series([_draw("2025-12-01", HDL_mgdl=60),
                                    _draw("2026-05-01", HDL_mgdl=40)]))
    assert _traj(a, "HDL").direction == "worsening"


def test_small_change_is_stable():
    """A change within the display-noise deadband reads as stable, not worsening."""
    a = analyze_series(make_series([_draw("2025-12-01", LDL_mgdl=100),
                                    _draw("2026-05-01", LDL_mgdl=101)]))
    assert _traj(a, "LDL").direction == "stable"


def test_single_point_is_insufficient_data():
    a = analyze_series(make_series([_draw("2026-05-01", LDL_mgdl=120)]))
    assert _traj(a, "LDL").direction == "insufficient_data"


def test_missing_values_excluded_from_direction():
    """A biomarker present in only one draw can't have a direction."""
    a = analyze_series(make_series([_draw("2025-12-01", HbA1c_pct=None),
                                    _draw("2026-05-01", HbA1c_pct=5.9)]))
    assert _traj(a, "HbA1c").direction == "insufficient_data"
    assert _traj(a, "HbA1c").n_points == 1


# --------------------------------------------------------------------------
# Change magnitude & rate
# --------------------------------------------------------------------------

def test_change_absolute():
    a = analyze_series(make_series([_draw("2025-12-01", LDL_mgdl=162),
                                    _draw("2026-05-01", LDL_mgdl=124)]))
    assert _traj(a, "LDL").change_absolute == -38


def test_change_absolute_none_for_single_point():
    a = analyze_series(make_series([_draw("2026-05-01", LDL_mgdl=120)]))
    assert _traj(a, "LDL").change_absolute is None


def test_rate_per_year_sign_and_magnitude():
    """100 -> 150 over exactly one year is +50/yr."""
    a = analyze_series(make_series([_draw("2025-05-01", LDL_mgdl=100),
                                    _draw("2026-05-01", LDL_mgdl=150)]))
    rate = _traj(a, "LDL").change_per_year
    assert rate is not None
    assert 49 < rate < 51


def test_rate_per_year_none_for_single_point():
    a = analyze_series(make_series([_draw("2026-05-01", LDL_mgdl=120)]))
    assert _traj(a, "LDL").change_per_year is None


# --------------------------------------------------------------------------
# Category transitions (reuse the clinical classifier)
# --------------------------------------------------------------------------

def test_prediabetes_to_normal_transition():
    """HbA1c 5.9 (Prediabetes) -> 5.4 (Normal) is one transition."""
    a = analyze_series(make_series([_draw("2025-12-01", HbA1c_pct=5.9),
                                    _draw("2026-05-01", HbA1c_pct=5.4)]))
    transitions = _traj(a, "HbA1c").transitions
    assert len(transitions) == 1
    assert transitions[0].from_category == "Prediabetes"
    assert transitions[0].to_category == "Normal"


def test_no_transition_when_category_unchanged():
    a = analyze_series(make_series([_draw("2025-12-01", LDL_mgdl=95),
                                    _draw("2026-05-01", LDL_mgdl=98)]))
    assert _traj(a, "LDL").transitions == ()


def test_point_categories_match_classifier():
    """Per-point category comes from the clinical core, not a reimplementation."""
    a = analyze_series(make_series([_draw("2026-05-01", LDL_mgdl=165)]))
    pt = _traj(a, "LDL").points[0]
    assert pt.category == "High"        # 165 -> High per appendix
    assert pt.category_tone in {"normal", "elevated", "high", "missing"}


def test_missing_point_has_missing_tone():
    a = analyze_series(make_series([_draw("2026-05-01", LDL_mgdl=None)]))
    pt = _traj(a, "LDL").points[0]
    assert pt.value is None
    assert pt.category is None
    assert pt.category_tone == "missing"


# --------------------------------------------------------------------------
# Interventions
# --------------------------------------------------------------------------

def test_intervention_detected_on_med_start():
    a = analyze_series(make_series([
        _draw("2025-12-01", LDL_mgdl=162, chol_med=False),
        _draw("2026-05-01", LDL_mgdl=124, chol_med=True),
    ]))
    assert len(a.interventions) == 1
    iv = a.interventions[0]
    assert iv.draw_date == dt.date(2026, 5, 1)
    assert "cholesterol" in iv.change.lower()
    assert "LDL" in iv.affected_biomarkers


def test_intervention_effect_is_descriptive_not_causal():
    a = analyze_series(make_series([
        _draw("2025-12-01", LDL_mgdl=162, chol_med=False),
        _draw("2026-05-01", LDL_mgdl=124, chol_med=True),
    ]))
    effects = " ".join(a.interventions[0].observed_effects).lower()
    # describes the observed change...
    assert "162" in effects and "124" in effects
    # ...but makes no causal/working claim
    for forbidden in ["lowered", "is working", "because", "caused", "due to the medication"]:
        assert forbidden not in effects


def test_no_intervention_when_no_med_change():
    a = analyze_series(make_series([
        _draw("2025-12-01", chol_med=True),
        _draw("2026-05-01", chol_med=True),
    ]))
    assert a.interventions == ()


def test_bp_med_affects_only_bp_biomarkers():
    a = analyze_series(make_series([
        _draw("2025-12-01", bp_med=False),
        _draw("2026-05-01", bp_med=True),
    ]))
    affected = set(a.interventions[0].affected_biomarkers)
    assert affected == {"SBP", "DBP"}


# --------------------------------------------------------------------------
# Structure & completeness
# --------------------------------------------------------------------------

def test_all_nine_biomarkers_present():
    a = analyze_series(make_series([_draw("2026-05-01")]))
    assert {t.biomarker for t in a.trajectories} == {
        "LDL", "HDL", "TG", "TC", "HbA1c", "FPG", "SBP", "DBP", "BMI"}


def test_points_sorted_by_date():
    a = analyze_series(make_series([_draw("2026-05-01", LDL_mgdl=120),
                                    _draw("2025-12-01", LDL_mgdl=100)]))
    dates = [p.draw_date for p in _traj(a, "LDL").points]
    assert dates == sorted(dates)


# --------------------------------------------------------------------------
# Safety guardrails — descriptive, NOT predictive (NFR3)
# --------------------------------------------------------------------------

def _all_strings(analysis: SeriesAnalysis) -> str:
    parts: list[str] = []
    for t in analysis.trajectories:
        parts.append(t.direction)
        for tr in t.transitions:
            parts += [tr.from_category, tr.to_category]
    for iv in analysis.interventions:
        parts.append(iv.change)
        parts += list(iv.observed_effects)
    return " ".join(parts).lower()


def test_no_predictive_or_causal_language_anywhere():
    a = analyze_series(make_series([
        _draw("2025-12-01", LDL_mgdl=162, HbA1c_pct=6.0, chol_med=False),
        _draw("2026-05-01", LDL_mgdl=124, HbA1c_pct=5.5, chol_med=True),
    ]))
    text = _all_strings(a)
    forbidden = [
        "will reach", "will develop", "predict", "expected to", "is working",
        "% risk", "risk of", "forecast", "projected", "by 2027", "by 2028",
        "guarantee", "cured", "lowered your", "caused",
    ]
    for phrase in forbidden:
        assert phrase not in text, f"Predictive/causal phrase leaked: {phrase!r}"


def test_direction_is_a_known_enum():
    a = analyze_series(make_series([_draw("2025-12-01", LDL_mgdl=100),
                                    _draw("2026-05-01", LDL_mgdl=150)]))
    for t in a.trajectories:
        assert t.direction in {"improving", "worsening", "stable", "insufficient_data"}


def test_no_future_dates_in_output():
    today = dt.date.today()
    a = analyze_series(make_series([_draw("2025-12-01"), _draw("2026-05-01")]))
    for t in a.trajectories:
        for p in t.points:
            assert p.draw_date <= today
    for iv in a.interventions:
        assert iv.draw_date <= today
