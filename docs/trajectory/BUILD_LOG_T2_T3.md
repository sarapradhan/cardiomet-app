# Build Log — Trajectory Tracking, Phases T2–T3

Record of the TDD cycle and persona reviews for the trajectory API (T2) and the
frontend timeline (T3). Same methodology as T0–T1: design-first, test-first,
independent persona review.

## TDD cycle

### T2 — stateless API endpoint
- Wrote `tests/test_trajectory_api.py` (17 tests) FIRST.
- RED: endpoint absent — 16 failed / 1 passed (404s, missing fields).
- Implemented `api/models/series.py`, `api/models/trajectory.py`,
  `api/routers/trajectory.py`; registered in `api/main.py`.
- GREEN: 17/17.
- Mirrored the contract into `frontend/src/lib/types.ts` (7 new interfaces) and
  added `submitSeries()` to `api/api.ts`.

### T3 — frontend timeline
- Built `frontend/src/lib/healthFile.ts` (export/import + user-controlled local
  cache), `components/Timeline.tsx` (SVG small-multiples), `components/
  TrajectorySummary.tsx`, `app/timeline/page.tsx`; added Timeline to nav.
- Fixed one TS error (BiomarkerInput → record cast for value counting).
- GREEN: `npm run type-check` clean; production build generates 7/7 pages incl.
  `/timeline`.
- Live check: posted a real 2-draw series over HTTP — LDL improving (High →
  Near Optimal), HbA1c Prediabetes → Normal, intervention surfaced, cohort label
  + disclaimer present.

### Regression & E2E
- Added a trajectory case to `tests/test_e2e.py` (real uvicorn over HTTP).
- Full suite: 243 tests pass.
- Validation gate: all tiers + type-check + descriptive-only scan PASS.

## Persona reviews — all PASS, no Blockers

### Staff Engineer
- Router is thin: zero clinical references; delegates to `analyze_series`. ✓
- Stateless: no DB/file writes/global mutation. ✓
- Faithful mapping via `dataclasses.asdict`. ✓

### Data & QA Auditor
- `types.ts` mirrors all 7 new Pydantic models exactly. ✓
- Zero new thresholds in T2/T3. ✓

### Clinical & Safety Reviewer
- Response model carries `cohort_label` Literal + required `disclaimer`. ✓
- Frontend renders disclaimer + "few draws can mislead" limitation unconditionally. ✓
- No predictive/causal/advice copy in any trajectory component. ✓

### Frontend/UX Engineer
- No clinical logic in the browser — presentation only. ✓
- Honest data-ownership copy ("your data stays on your device"). ✓
- Accessibility: chart `role="img"` + `aria-label`; error `role="alert"`; labeled inputs. ✓

## Outcome
T2–T3 complete. Stateless trajectory endpoint and the timeline UI implemented,
fully tested (243 total green), gate-passing, and cleared by four persona
reviews with no Blockers. The differentiation capability (longitudinal,
verifiable, user-owned tracking) is now end-to-end.

## Remaining (T4 closeout)
Browser-tier manual walkthrough per docs/E2E_CHECKLIST.md (timeline section);
update ARCHITECTURE.md with the new endpoint/route/components.
