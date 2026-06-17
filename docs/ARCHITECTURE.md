# SAHC RiskLens — Architecture

## Stack
Next.js 14 + TypeScript + Tailwind + Material Design 3 → Vercel
FastAPI + Pydantic v2 → Railway
sahc_risklens/ (Python clinical logic) → no web framework

## Request Flow
Browser → Next.js (Vercel) → POST /api/v1/benchmark → FastAPI (Railway)
                                                      → sahc_risklens/
                                                        thresholds.py
                                                        nhanes_loader.py
                                                        percentile.py
                                                      → BenchmarkResponse
                                                        cohort_label: "NHANES Non-Hispanic Asian"
                                                        disclaimer: (required, always present)
                                                      → Next.js renders results

## API Contract Sync Rule
api/models/results.py (Pydantic, authoritative)
frontend/src/lib/types.ts (TypeScript mirror)
When results.py changes, update types.ts in the same session.
cohort_label: Literal["NHANES Non-Hispanic Asian"] — enforced by type system.
disclaimer: required Pydantic field, min_length=20 — cannot be absent.

## Frontend Design System
Material Design 3 (minimalistic):
- Colors: md-primary #1565C0, md-surface #FFFFFF, md-background #F5F5F5
- Elevation: box-shadows at 1dp/2dp/3dp
- Shape: rounded corners (4px/8px/12px/16px/28px scale)
- Typography: Inter — light weights for headings, medium for labels
- Components: md-card, md-button-primary, md-button-outlined, md-chip, md-label
- Clinical chips: chip-normal/chip-elevated/chip-high/chip-missing

## Phase 1 Deployment
Vercel (frontend, free) + Railway (backend, free starter)

## Phase 2 Infrastructure
See docs/PHASE2_ROADMAP.md
Recommended: Vercel Pro ($20/mo) + Railway Hobby ($5/mo) → GitHub Actions CI/CD
