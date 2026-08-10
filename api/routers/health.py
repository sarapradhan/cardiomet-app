"""api/routers/health.py — GET /health"""
from __future__ import annotations

from fastapi import APIRouter

from sahc_risklens.config import NHANES_DATA_DIR

router = APIRouter()

@router.get("/health")
def health_check() -> dict:
    loaded = (NHANES_DATA_DIR / "DEMO_J.XPT").exists()
    return {"status": "ok", "version": "0.1.0",
            "nhanes_loaded": loaded, "mode": "live" if loaded else "demo"}
