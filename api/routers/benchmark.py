"""
api/routers/benchmark.py — POST /api/v1/benchmark.

Thin orchestration layer: validate input (Pydantic), call sahc_risklens/ for all
clinical and benchmark logic, assemble BenchmarkResponse. No clinical logic,
thresholds, or NHANES variable names appear here — those live in sahc_risklens/.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.models.patient import BiomarkerInput
from api.models.results import BenchmarkResponse
from sahc_risklens.benchmark.percentile import SUPPORTED_COHORTS, get_benchmark_data
from sahc_risklens.clinical.biomarkers import find_missing_biomarkers
from sahc_risklens.clinical.disclaimers import (
    build_physician_guide,
    get_medication_notes,
)
from sahc_risklens.clinical.care_navigation import get_care_navigation
from sahc_risklens.clinical.south_asian_context import get_south_asian_context
from sahc_risklens.clinical.thresholds import (
    classify_all_biomarkers,
    classify_risk_enhancing_markers,
)
from sahc_risklens.config import DEFAULT_COHORT, cohort_label

router = APIRouter()


@router.post("/benchmark", response_model=BenchmarkResponse)
def benchmark_biomarkers(
    data: BiomarkerInput,
    cohort: str = Query(
        DEFAULT_COHORT,
        description=(
            "Reference cohort to benchmark against. "
            f"One of: {', '.join(SUPPORTED_COHORTS)}. Defaults to NHANES."
        ),
    ),
    match: bool = Query(
        False,
        description=(
            "If true, benchmark each value against the patient's matched peer "
            "subgroup (sex + age band + medication use), like the original SCORE "
            "tool, with small-cell suppression and transparent fallback. Requires "
            "sex and age_yr in the body; unavailable for the NHANES cohort."
        ),
    ),
) -> BenchmarkResponse:
    """
    Return threshold classifications, the selected reference benchmark, South
    Asian risk context, a template-based physician discussion guide, medication
    notes, and missing-biomarker flags.

    The `cohort` query parameter selects the benchmark population (default NHANES
    Non-Hispanic Asian). Classification thresholds are guideline-based and do not
    change with the cohort. Educational only — not diagnostic; cohort_label and
    disclaimer are always present.
    """
    if cohort not in SUPPORTED_COHORTS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown cohort {cohort!r}. Supported: {list(SUPPORTED_COHORTS)}.",
        )

    threshold_results = classify_all_biomarkers(data)
    risk_enhancing_markers = classify_risk_enhancing_markers(data)
    benchmark_data = get_benchmark_data(data, cohort=cohort, match=match)
    any_matched = next((p for p in benchmark_data if p["matched"]), None)
    missing_biomarkers = find_missing_biomarkers(data)
    medication_notes = get_medication_notes(data)
    physician_guide = build_physician_guide(threshold_results)

    # South Asian context only when the patient indicated South Asian ancestry.
    south_asian_context: list = []
    if getattr(data, "south_asian", None):
        south_asian_context = get_south_asian_context(
            bmi_value=data.BMI_kgm2, lpa_value=data.Lpa_mgdl
        )

    return BenchmarkResponse(
        threshold_results=threshold_results,
        risk_enhancing_markers=risk_enhancing_markers,
        benchmark_data=benchmark_data,
        south_asian_context=south_asian_context,
        physician_guide=physician_guide,
        care_navigation=get_care_navigation(data),
        missing_biomarkers=missing_biomarkers,
        medication_notes=medication_notes,
        cohort=cohort,
        cohort_label=cohort_label(cohort),
        matched=any_matched is not None,
        match_description=any_matched["match_description"] if any_matched else None,
    )
