"""api/main.py — FastAPI entry point. Thin layer over sahc_risklens/."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import benchmark, health, thresholds, trajectory

app = FastAPI(
    title="SAHC RiskLens API",
    description="Responsible cardiometabolic benchmarking. Educational use only — not diagnostic.",
    version="0.1.0",
)

# CORS. ALLOWED_ORIGINS is the exact-match allowlist. ALLOWED_ORIGIN_REGEX
# exists because preview deployments get a freshly generated hostname on every
# build (e.g. https://<project>-<hash>-<team>.vercel.app), so no static list can
# ever cover them — without a regex every preview fails CORS preflight with
# "Disallowed CORS origin" and the UI reports a bare "Failed to fetch".
# Both are unset by default: a deployment that configures neither keeps the
# local-dev origins only, which is the safe default.
_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
_origin_regex = (os.getenv("ALLOWED_ORIGIN_REGEX") or "").strip() or None
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_origin_regex=_origin_regex,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)
app.include_router(benchmark.router, prefix="/api/v1", tags=["benchmark"])
app.include_router(thresholds.router, prefix="/api/v1", tags=["thresholds"])
app.include_router(trajectory.router, prefix="/api/v1", tags=["trajectory"])


# --- Single-container static serving -------------------------------------
# When the frontend has been exported to frontend/out (production container),
# serve it at the root so one service delivers both the UI and the API.
# In local two-server dev this directory is absent and only the API runs.
_FRONTEND_OUT = Path(__file__).resolve().parent.parent / "frontend" / "out"
if _FRONTEND_OUT.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_OUT), html=True), name="frontend")
