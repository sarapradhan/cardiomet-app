"""
api/routers/thresholds.py — GET /api/v1/thresholds.

Returns the complete clinical threshold reference table. Thin wrapper over
sahc_risklens.clinical.thresholds.get_all_threshold_categories().
"""
from __future__ import annotations

from fastapi import APIRouter

from api.models.results import ThresholdsResponse
from sahc_risklens.clinical.thresholds import get_all_threshold_categories

router = APIRouter()


@router.get("/thresholds", response_model=ThresholdsResponse)
def get_thresholds() -> ThresholdsResponse:
    """Complete threshold categories per biomarker, sourced from CLINICAL_LOGIC_APPENDIX.md."""
    return ThresholdsResponse(**get_all_threshold_categories())
