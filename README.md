---
title: SAHC RiskLens
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
short_description: Educational South Asian cardiometabolic lab context — not a diagnosis
---

# SAHC RiskLens

**Responsible cardiometabolic benchmarking for South Asian heart health.**
Educational only · Does not diagnose · Discuss results with your clinician.

## Stack
Next.js 14 + TypeScript + Tailwind + Material Design 3 → Vercel
FastAPI + Pydantic v2 → Railway

## Quick Start
```bash
bash scripts/setup_env.sh
source .venv/bin/activate
python scripts/download_nhanes.py
# Terminal 1: uvicorn api.main:app --reload    → http://localhost:8000/docs
# Terminal 2: cd frontend && npm run dev       → http://localhost:3000
```

## Key Rules
- NHANES variables → DATA_DICTIONARY.md only
- Threshold values → CLINICAL_LOGIC_APPENDIX.md only
- cohort_label → always "NHANES Non-Hispanic Asian" (Pydantic Literal)
- disclaimer → required, always rendered, never suppressed
- API change → update results.py AND types.ts together
- Session start → read SESSION_START_PROMPT.md

## Validation Gate
```bash
bash scripts/run_validation_gate.sh
```

## Docs
docs/PRD.md · docs/ARCHITECTURE.md · docs/DATA_DICTIONARY.md ·
docs/CLINICAL_LOGIC_APPENDIX.md · docs/SAFETY_AND_LIMITATIONS.md ·
docs/PHASE2_ROADMAP.md · docs/SESSION_STATUS.md
