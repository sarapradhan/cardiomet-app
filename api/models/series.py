"""
api/models/series.py — Pydantic v2 input models for the trajectory endpoint.

Wraps the existing BiomarkerInput with a draw date. frontend/src/lib/types.ts
BiomarkerDraw / BiomarkerSeries must mirror these.
"""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field, field_validator

from api.models.patient import BiomarkerInput


class BiomarkerDrawIn(BaseModel):
    draw_date: dt.date
    values: BiomarkerInput
    label: str | None = Field(None, max_length=120)

    @field_validator("draw_date")
    @classmethod
    def _no_future_dates(cls, v: dt.date) -> dt.date:
        if v > dt.date.today():
            raise ValueError("draw_date cannot be in the future")
        return v


class BiomarkerSeriesIn(BaseModel):
    draws: list[BiomarkerDrawIn] = Field(min_length=1)

    model_config = {"json_schema_extra": {"example": {
        "draws": [
            {"draw_date": "2025-12-01", "label": "baseline",
             "values": {"LDL_mgdl": 162, "HbA1c_pct": 6.0, "sex": "M",
                        "south_asian": True, "chol_med": False}},
            {"draw_date": "2026-05-01", "label": "after starting statin",
             "values": {"LDL_mgdl": 124, "HbA1c_pct": 5.5, "sex": "M",
                        "south_asian": True, "chol_med": True}},
        ]
    }}}
