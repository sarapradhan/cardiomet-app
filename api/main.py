"""api/main.py — FastAPI entry point. Thin layer over sahc_risklens/."""
from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import benchmark, thresholds, health

app = FastAPI(
    title="SAHC RiskLens API",
    description="Responsible cardiometabolic benchmarking. Educational use only — not diagnostic.",
    version="0.1.0",
)

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)
app.include_router(benchmark.router, prefix="/api/v1", tags=["benchmark"])
app.include_router(thresholds.router, prefix="/api/v1", tags=["thresholds"])
