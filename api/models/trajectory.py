"""
api/models/trajectory.py — Pydantic v2 output models for POST /api/v1/trajectory.

AUTHORITATIVE output contract for the trajectory endpoint. Mirrors the T1
dataclasses in sahc_risklens/trajectory/analytics.py field-for-field, and is
itself mirrored in frontend/src/lib/types.ts. Carries the same safety fields as
BenchmarkResponse (cohort_label Literal, required disclaimer).
"""
from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from sahc_risklens.config import NHANES_COHORT_LABEL, PRODUCT_DISCLAIMER


class TrajectoryPointOut(BaseModel):
    draw_date: dt.date
    value: float | None
    category: str | None
    category_tone: str


class CategoryTransitionOut(BaseModel):
    from_category: str
    to_category: str
    from_date: dt.date
    to_date: dt.date


class BiomarkerTrajectoryOut(BaseModel):
    biomarker: str
    unit: str
    points: list[TrajectoryPointOut]
    direction: str
    change_absolute: float | None
    change_per_year: float | None
    transitions: list[CategoryTransitionOut]
    n_points: int


class InterventionMarkerOut(BaseModel):
    draw_date: dt.date
    change: str
    affected_biomarkers: list[str]
    observed_effects: list[str]


class TrajectoryResponse(BaseModel):
    trajectories: list[BiomarkerTrajectoryOut]
    interventions: list[InterventionMarkerOut]
    cohort_label: Literal["NHANES Non-Hispanic Asian"] = NHANES_COHORT_LABEL  # type: ignore[assignment]
    disclaimer: str = Field(default=PRODUCT_DISCLAIMER, min_length=20)
    validation_status: str = "Phase 1 — Demo"
