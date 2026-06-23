"""
api/models/results.py — Pydantic v2 output models.
AUTHORITATIVE API output contract.
frontend/src/lib/types.ts must mirror every field in BenchmarkResponse exactly.
When this file changes, update types.ts in the same session.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from sahc_risklens.config import (
    DEFAULT_COHORT,
    NHANES_COHORT_LABEL,
    PRODUCT_DISCLAIMER,
    SAHC_COHORT_LABEL,
)

# The set of honest cohort labels a benchmark response may carry. Each is tied to
# a real, separately-documented cohort; the NHANES label is never applied to the
# SAHC cohort or vice versa (see sahc_risklens/benchmark/percentile.py).
CohortLabel = Literal[
    "NHANES Non-Hispanic Asian",
    "South Asian Heart Center clinical cohort",
]


class ThresholdResult(BaseModel):
    biomarker: str
    value: float | None
    unit: str
    category: str | None
    category_description: str
    guideline_source: str
    note: str | None = None


class BenchmarkPoint(BaseModel):
    biomarker: str
    patient_value: float | None
    cohort_p10: float
    cohort_p25: float
    cohort_median: float
    cohort_p75: float
    cohort_p90: float
    cohort_label: CohortLabel = NHANES_COHORT_LABEL
    cohort_n: int
    # Peer matching (SCORE-style). When matched is True, the cohort_* fields
    # above describe the patient's matched subgroup (sex + age band + medication),
    # not the whole cohort; match_n is that subgroup's size and match_description
    # names it (e.g. "Women, 49–64"). When False, the whole-cohort distribution is
    # shown (matching was not requested, unavailable, or the cell was too small).
    matched: bool = False
    match_n: int | None = None
    match_description: str | None = None


class SouthAsianContextItem(BaseModel):
    factor: str
    description: str
    guideline_source: str


class PhysicianGuideItem(BaseModel):
    biomarker: str
    category: str
    discussion_prompt: str
    guideline_note: str


class BenchmarkResponse(BaseModel):
    threshold_results: list[ThresholdResult]
    benchmark_data: list[BenchmarkPoint]
    south_asian_context: list[SouthAsianContextItem]
    physician_guide: list[PhysicianGuideItem]
    missing_biomarkers: list[str]
    medication_notes: list[str]
    cohort: str = DEFAULT_COHORT  # selected cohort id (config.COHORT_*)
    cohort_label: CohortLabel = NHANES_COHORT_LABEL
    matched: bool = False               # True if peer matching was applied to >=1 biomarker
    match_description: str | None = None  # peer group used, e.g. "Women, 49–64, on cholesterol medication"
    disclaimer: str = Field(default=PRODUCT_DISCLAIMER, min_length=20)
    validation_status: str = "Phase 1 — Demo"


class ThresholdCategory(BaseModel):
    category: str
    range_description: str
    guideline_source: str


class ThresholdsResponse(BaseModel):
    LDL: list[ThresholdCategory]
    HDL: list[ThresholdCategory]
    TG: list[ThresholdCategory]
    TC: list[ThresholdCategory]
    HbA1c: list[ThresholdCategory]
    FPG: list[ThresholdCategory]
    SBP: list[ThresholdCategory]
    DBP: list[ThresholdCategory]
    BMI_standard: list[ThresholdCategory]
    BMI_south_asian_context: list[ThresholdCategory]
