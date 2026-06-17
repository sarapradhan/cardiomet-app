"""
api/routers/trajectory.py — POST /api/v1/trajectory.

Thin, stateless: validate the posted series, convert to the core BiomarkerSeries,
call the T1 analytics engine, and map the dataclasses to the Pydantic response.
No analytics, thresholds, or NHANES variable names here. Stores nothing.
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from api.models.series import BiomarkerSeriesIn
from api.models.trajectory import TrajectoryResponse
from sahc_risklens.trajectory.analytics import analyze_series
from sahc_risklens.trajectory.series import (
    BiomarkerDraw,
    SeriesValidationError,
    make_series,
)

router = APIRouter()


@router.post("/trajectory", response_model=TrajectoryResponse)
def trajectory(series_in: BiomarkerSeriesIn) -> TrajectoryResponse:
    """
    Descriptive longitudinal trajectories across a series of dated draws.
    Educational only — not diagnostic, not predictive. Stateless: the server
    computes on the posted series and stores nothing.
    """
    try:
        series = make_series([
            BiomarkerDraw(
                draw_date=d.draw_date,
                values=d.values.model_dump(),
                label=d.label,
            )
            for d in series_in.draws
        ])
    except SeriesValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    analysis = analyze_series(series)

    # dataclasses.asdict converts the nested frozen dataclasses to dicts that
    # match the Pydantic output models field-for-field.
    return TrajectoryResponse(
        trajectories=[asdict(t) for t in analysis.trajectories],
        interventions=[asdict(i) for i in analysis.interventions],
    )
