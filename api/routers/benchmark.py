"""
api/routers/benchmark.py — POST /api/v1/benchmark.

Thin orchestration layer: validate input (Pydantic), call sahc_risklens/ for all
clinical and benchmark logic, assemble BenchmarkResponse. No clinical logic,
thresholds, or NHANES variable names appear here — those live in sahc_risklens/.
"""
from __future__ import annotations

from fastapi import APIRouter

from api.models.patient import BiomarkerInput
from api.models.results import BenchmarkResponse
from sahc_risklens.benchmark.percentile import get_benchmark_data
from sahc_risklens.clinical.biomarkers import find_missing_biomarkers
from sahc_risklens.clinical.disclaimers import (
    build_physician_guide,
    get_medication_notes,
)
from sahc_risklens.clinical.south_asian_context import get_south_asian_context
from sahc_risklens.clinical.thresholds import classify_all_biomarkers

router = APIRouter()


@router.post("/benchmark", response_model=BenchmarkResponse)
def benchmark_biomarkers(data: BiomarkerInput) -> BenchmarkResponse:
    """
    Return threshold classifications, the NHANES Non-Hispanic Asian benchmark,
    South Asian risk context, a template-based physician discussion guide,
    medication notes, and missing-biomarker flags.

    Educational only — not diagnostic. cohort_label and disclaimer are supplied
    by the response model defaults and always present.
    """
    threshold_results = classify_all_biomarkers(data)
    benchmark_data = get_benchmark_data(data)
    missing_biomarkers = find_missing_biomarkers(data)
    medication_notes = get_medication_notes(data)
    physician_guide = build_physician_guide(threshold_results)

    # South Asian context only when the patient indicated South Asian ancestry.
    south_asian_context: list = []
    if getattr(data, "south_asian", None):
        south_asian_context = get_south_asian_context(bmi_value=data.BMI_kgm2)

    return BenchmarkResponse(
        threshold_results=threshold_results,
        benchmark_data=benchmark_data,
        south_asian_context=south_asian_context,
        physician_guide=physician_guide,
        missing_biomarkers=missing_biomarkers,
        medication_notes=medication_notes,
    )
