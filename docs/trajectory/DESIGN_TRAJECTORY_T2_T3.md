# PRD + Technical Design — Trajectory Tracking, Phases T2–T3

> Design-before-code document for the API endpoint (T2) and the frontend timeline (T3). Parent: `docs/INCREMENTAL_VALUE_SPEC.md`, `docs/IMPLEMENTATION_PLAN_TIMELINE.md`. Builds on the T0–T1 clinical core (`sahc_risklens/trajectory/`).

## 1. Objective
Expose the trajectory engine over a **stateless** HTTP endpoint (T2) and give users a **timeline UI** with user-owned data (T3) — so a person can enter several dated draws (or import their health file), see how their values move over time against guideline bands, and own their data with nothing stored server-side.

## 2. Users
- **The patient (Priya/Rajesh)** — enters multiple dated draws or imports a health file; reads the timeline; exports their file.
- **Downstream/maintainer** — relies on the contract mirror (Pydantic ↔ TypeScript) staying in sync.
- **Reviewers** — Staff Engineer, Data & QA, Clinical & Safety, plus a Frontend/UX persona for T3.

## 3. Functional requirements

### T2 — API
- **FR-T2.1** `POST /api/v1/trajectory` accepts a series of dated draws and returns a `TrajectoryResponse`.
- **FR-T2.2** Input validated by Pydantic: each draw has a `draw_date` (no future dates) and the existing `BiomarkerInput` panel; empty series rejected (422).
- **FR-T2.3** Response carries the same safety fields as `/benchmark`: `cohort_label` Literal and a required `disclaimer`, plus `validation_status`.
- **FR-T2.4** Endpoint is **stateless** — computes on the posted series, returns, stores nothing.
- **FR-T2.5** The router is thin: validate → convert to core `BiomarkerSeries` → `analyze_series()` → map dataclasses to Pydantic. No analytics in the router.

### T3 — Frontend
- **FR-T3.1** A `/timeline` page where the user adds multiple dated draws across a session.
- **FR-T3.2** A `Timeline` component: per-biomarker sparkline over time with guideline category bands behind it, the user's points plotted, and intervention markers.
- **FR-T3.3** A `TrajectorySummary` component: plain-language per-biomarker summary (direction, change, transitions) + intervention notes, with an always-on disclaimer and a "few draws can mislead" limitation.
- **FR-T3.4** Export the series to a user-owned health-file JSON (download); import one back; optional local-browser cache with an explicit "clear" control.
- **FR-T3.5** `types.ts` mirrors every new Pydantic model in the same change.

## 4. Non-functional requirements
- **NFR1** Stateless server (no DB, no accounts) — preserves the privacy posture.
- **NFR2** Contract sync: Pydantic models in `api/models/` mirrored exactly in `frontend/src/lib/types.ts`; `npm run type-check` must pass.
- **NFR3** Descriptive-only safety carries through the API and UI (no predictive/causal/risk language in any served or rendered string).
- **NFR4** No clinical logic in the browser; the frontend renders what the API returns.
- **NFR5** TDD for T2 (tests first). T3 verified by type-check + production build + an automated browser-tier check where feasible, plus the existing manual E2E checklist.

## 5. Out of scope
Server-side persistence/accounts; predictive projection; PDF export (future); auth.

## 6. Technical design

### 6.1 T2 — API models (`api/models/series.py`, `api/models/trajectory.py`)
Input:
```
BiomarkerDrawIn:   draw_date: date (<= today); values: BiomarkerInput; label: str | None
BiomarkerSeriesIn: draws: list[BiomarkerDrawIn]  (min_length=1)
```
Output (mirrors the T1 dataclasses field-for-field):
```
TrajectoryPointOut(draw_date, value, category, category_tone)
CategoryTransitionOut(from_category, to_category, from_date, to_date)
BiomarkerTrajectoryOut(biomarker, unit, points[], direction, change_absolute, change_per_year, transitions[], n_points)
InterventionMarkerOut(draw_date, change, affected_biomarkers[], observed_effects[])
TrajectoryResponse(trajectories[], interventions[],
                   cohort_label: Literal["NHANES Non-Hispanic Asian"],
                   disclaimer: str (min_length=20), validation_status: str)
```
`draw_date` future-rejection is enforced both by a Pydantic validator (fast 422) and again by the core `make_series` (defense in depth).

### 6.2 T2 — router (`api/routers/trajectory.py`)
```
POST /api/v1/trajectory
  parse BiomarkerSeriesIn
  -> [BiomarkerDraw(draw_date, values=draw.values.model_dump(), label) ...]
  -> make_series(...)            # may raise SeriesValidationError -> 422
  -> analyze_series(...)          # T1 engine
  -> map SeriesAnalysis dataclasses -> TrajectoryResponse
  return
```
Registered in `api/main.py` under `/api/v1`, tag `trajectory`.

### 6.3 T3 — components & libs
- `frontend/src/lib/types.ts` — add `BiomarkerDraw`, `BiomarkerSeries`, and all trajectory response interfaces.
- `frontend/src/lib/api.ts` — add `submitSeries(series): Promise<TrajectoryResponse>`.
- `frontend/src/lib/healthFile.ts` — `exportHealthFile(series)` (triggers JSON download), `parseHealthFile(text)` (validate + return series), `saveLocal/loadLocal/clearLocal` (browser cache, user-controlled).
- `frontend/src/components/Timeline.tsx` — small-multiples SVG sparklines; category bands derived from the points' tones; intervention flags on the date axis. Pure presentation, MD3 tokens.
- `frontend/src/components/TrajectorySummary.tsx` — plain-language summary + disclaimer + few-draws limitation.
- `frontend/src/app/timeline/page.tsx` — add-draws flow, calls `submitSeries`, renders `Timeline` + `TrajectorySummary`, export/import controls.
- `frontend/src/app/layout.tsx` — add "Timeline" nav link.

### 6.4 Safety carry-through
- The API never adds language; it maps the engine's already-descriptive strings.
- The UI's only new copy is the disclaimer (reused) and a new limitation: "A small number of draws can be misleading; lab values vary for many reasons; trends are discussion context, not conclusions." No projection, no advice.

## 7. Test plan
- **T2 (TDD):** `tests/test_trajectory_api.py` — full contract; safety fields; multi-draw correctness; 422 on empty/future/bad; per-point category cross-check vs `/benchmark`; statelessness (repeat calls identical, no side effects).
- **E2E:** extend `tests/test_e2e.py` — real server, POST a series, assert contract + safety invariants over HTTP.
- **T3:** `npm run type-check` + production `npm run build`; manual/automated page-render checks; `docs/E2E_CHECKLIST.md` timeline section.

## 8. Persona review gates
- **Staff Engineer** — thin router, contract mirror exact, stateless.
- **Data & QA Auditor** — response faithfully reflects engine; no new thresholds; type mirror complete.
- **Clinical & Safety Reviewer** — served + rendered strings descriptive-only; disclaimer + limitations always present.
- **Frontend/UX Engineer** — accessible, responsive, MD3-consistent, no clinical logic in browser, honest data-ownership copy.
