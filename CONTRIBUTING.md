# Contributing & Engineering Guide — SAHC RiskLens

## Ground Truth Imports
@docs/CLINICAL_LOGIC_APPENDIX.md
@docs/DATA_DICTIONARY.md

## Operating Model
Main session = tech lead + implementer.
Subagents = independent reviewers — they do not write code unless explicitly asked.

## Architecture
| Layer | Technology | Directory |
|---|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind + Material Design | `frontend/` |
| Backend API | FastAPI + Pydantic v2 | `api/` |
| Clinical logic | Python | `sahc_risklens/` |

`sahc_risklens/` owns all business rules. API routers are thin wrappers.
Frontend calls the API — no clinical logic in the browser.

## Authority Hierarchy
1. Medical safety and clinical correctness.
2. `docs/PRD.md` over implementation convenience.
3. `docs/DATA_DICTIONARY.md` — only permitted NHANES variable names.
4. `docs/CLINICAL_LOGIC_APPENDIX.md` — only permitted threshold values.
5. `api/models/results.py` ↔ `frontend/src/lib/types.ts` must stay in sync.

Never invent a NHANES variable name or clinical threshold value.
API field change → update `results.py` AND `types.ts` in the same session.

## Medical Safety Rules
- No diagnosis, no treatment advice, no medication recommendations.
- `cohort_label` → always exactly `"NHANES Non-Hispanic Asian"` (Pydantic Literal).
- `disclaimer` → required field, min_length=20, always rendered in frontend.
- Physician discussion guide → rule-based template in Phase 1 (no LLM).
- Limitations panel → always visible, never suppressed.
- South Asian BMI thresholds → risk-context discussion only, never NHANES benchmark.

## Engineering — Python
- Business logic in `sahc_risklens/`. API routers: validate → call library → return.
- Pydantic v2 for all I/O models. Type hints on all functions.
- Docstrings cite guideline source on all clinical functions.
- Tests for every clinical or data logic change.

## Engineering — TypeScript
- Strict mode. No `any` types. All API types from `frontend/src/lib/types.ts`.
- `NEXT_PUBLIC_API_URL` only — never hardcode API URLs.
- No PHI/biomarker values in localStorage or cookies beyond current session.
- Always render `disclaimer` and `cohort_label` exactly as received from API.

## Session Continuity
Read `docs/SESSION_STATUS.md` at start. Update it at end.
Run `bash scripts/run_validation_gate.sh` before closing.
