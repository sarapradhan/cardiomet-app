# CardioMet Lens — Implementation Plan
## Longitudinal Trajectory Tracking ("CardioMet Lens Timeline")

> Companion to `INCREMENTAL_VALUE_SPEC.md`. This is the build plan: phases, concrete file-level tasks, tests, acceptance criteria, and sequencing. It follows the same milestone discipline (P-phases, reviewer subagents, validation gate) as the original Phase 1 build, so it slots into the existing engineering workflow.

---

## 0. Principles for this build (carry over from Phase 1)

- **Single source of truth.** No new clinical threshold is created. The trajectory engine reuses `sahc_risklens/clinical/thresholds.py` and `biomarkers.py`. If a per-point category is needed, it comes from `classify_all_biomarkers`, never a reimplementation.
- **Server stays stateless.** No database, no accounts. Persistence is user-owned (export/import + optional local browser cache). This keeps the regulatory gate low.
- **Descriptive, not predictive.** Safety guardrails from spec §6 are implemented as code and tests, not just intentions.
- **Contract sync.** Every new API model in `api/models/` is mirrored in `frontend/src/lib/types.ts` in the same change.
- **Nothing ships until the validation gate passes**, including the new trajectory tests and a Clinical & Safety Reviewer pass on the new copy/logic.

---

## Phase T0 — Foundations & data model
**Goal:** the types and series-handling exist and are tested, with no analytics yet.

| Task | File(s) | Detail |
|---|---|---|
| Create trajectory package | `sahc_risklens/trajectory/__init__.py` | New subpackage |
| Series model + validation | `sahc_risklens/trajectory/series.py` | `BiomarkerDraw`, `BiomarkerSeries`; sort ascending by `draw_date`; dedupe/period rules; reject empty series |
| API input models | `api/models/series.py` | Pydantic `BiomarkerDrawIn`, `BiomarkerSeriesIn` wrapping existing `BiomarkerInput`; `draw_date` validation (no future dates) |
| Health-file schema | `sahc_risklens/trajectory/health_file.py` | `HealthFile` (schema_version, exported_at, series); load/validate with clear errors on bad/old schema |
| Unit tests | `tests/test_series.py` | Sorting, dedupe, empty rejection, future-date rejection, health-file round-trip (export dict == import dict) |

**Acceptance:** `pytest tests/test_series.py` green; a series of dated draws validates, sorts, and round-trips through the health-file format. No analytics, no endpoint yet.

**Effort:** small. ~1 focused session.

---

## Phase T1 — Trajectory analytics engine
**Goal:** the descriptive analytics from spec §5, computed correctly and safely, reusing the clinical core.

| Task | File(s) | Detail |
|---|---|---|
| Direction + change | `sahc_risklens/trajectory/analytics.py` | Per biomarker: earliest→latest delta, consecutive deltas, direction (improving/worsening/stable/insufficient) honoring per-biomarker "higher is better" (HDL) vs worse; stability deadband |
| Rate of change | same | OLS slope per year; only when ≥2 dated points span time; return None otherwise |
| Category transitions | same | Per-draw category via `classify_all_biomarkers`; detect changes + the date interval |
| Intervention detection | same | Medication flag false→true between draws; reuse `clinical/thresholds._MED_AFFECTS`; descriptive observed effect only |
| Safety guardrails | same | No future-dated output; no causal/predictive strings; neutral direction language |
| Unit tests | `tests/test_trajectory_analytics.py` | Known fixtures with hand-computed expected slopes/directions/transitions; HDL direction-sense test; intervention-effect descriptive-only test; **guardrail tests**: assert no projection/causal/risk-score language in any output |

**Acceptance:** `pytest tests/test_trajectory_analytics.py` green; analytics match hand-computed values; guardrail tests prove output is descriptive-only. Engine imports the clinical core and introduces zero new thresholds.

**Effort:** medium. ~1–2 sessions. This is the analytical heart.

---

## Phase T2 — API endpoint
**Goal:** a stateless `POST /api/v1/trajectory` that turns a posted series into a `TrajectoryResponse`.

| Task | File(s) | Detail |
|---|---|---|
| Output models | `api/models/trajectory.py` | `TrajectoryPoint`, `BiomarkerTrajectory`, `InterventionMarker`, `TrajectoryResponse` (with `cohort_label` Literal + required `disclaimer`, mirroring existing safety fields) |
| Router | `api/routers/trajectory.py` | Thin: validate `BiomarkerSeriesIn` → call `trajectory.analytics` → assemble response; no logic in router |
| Register | `api/main.py` | Include the new router under `/api/v1` |
| Contract mirror | `frontend/src/lib/types.ts` | Add `BiomarkerDraw`, `BiomarkerSeries`, all trajectory response types — same change |
| Integration tests | `tests/test_trajectory_api.py` | Endpoint returns full contract; safety fields present; multi-draw scenario correctness; 422 on bad/empty/future series; cross-check per-point categories match `/benchmark` |

**Acceptance:** `pytest tests/test_trajectory_api.py` green; endpoint stateless (no writes anywhere); `cohort_label`/`disclaimer` always present; `npm run type-check` passes with the mirrored types.

**Effort:** small–medium. ~1 session.

---

## Phase T3 — Frontend: input, timeline, export/import
**Goal:** users can build a multi-draw history, see the timeline, and own their data file.

| Task | File(s) | Detail |
|---|---|---|
| Multi-draw input | `frontend/src/app/timeline/page.tsx` | Add dated draws across a session; list of draws with dates/labels; reuse `BiomarkerForm` per draw |
| Timeline component | `frontend/src/components/Timeline.tsx` | Small-multiples sparklines per biomarker; category bands behind; patient points; intervention markers; reuse MD3 tokens + `categoryStyles` |
| Trajectory summary | `frontend/src/components/TrajectorySummary.tsx` | Plain-language per-biomarker summary (delta, transitions, intervention notes); always-on disclaimer + new "few-draws" limitation |
| Health-file export/import | `frontend/src/lib/healthFile.ts` | Export series → downloadable JSON via File API; import + validate; optional local browser cache with explicit "clear my data" control |
| API client | `frontend/src/lib/api.ts` | Add `submitSeries()` → `/api/v1/trajectory` |
| Nav | `frontend/src/app/layout.tsx` | Add "Timeline" to the nav |

**Acceptance:** type-check + production build pass; manual walkthrough — add ≥2 dated draws, see timeline + summary, export a file, reload/import it, clear local data. Disclaimer and limitations always visible. No clinical logic in the browser.

**Effort:** medium–large. ~2 sessions (the timeline component is the one substantive new piece of UI).

---

## Phase T4 — Tests, gate, docs, review
**Goal:** the feature meets the same bar as Phase 1 and is releasable.

| Task | File(s) | Detail |
|---|---|---|
| Smoke coverage | `tests/test_smoke.py` | Add trajectory modules + endpoint to the smoke tier |
| E2E | `tests/test_e2e.py` | Real-server: post a series, assert full contract + safety invariants over HTTP |
| Validation gate | `scripts/run_validation_gate.sh` | Add trajectory test files to the tiered run; add a guardrail scan (no "will reach"/"predict"/causal-intervention phrasing in trajectory source) |
| Docs | `docs/` | Update `ARCHITECTURE.md` (new package/endpoint/component), `SAFETY_AND_LIMITATIONS.md` (few-draws + descriptive-only), `RELEASE_CHECKLIST.md` (trajectory items), `SESSION_STATUS.md` |
| Clinical & Safety review | `.project/agents/clinical_safety_reviewer.md` | Run the reviewer specifically on trajectory copy + intervention language; fix any Blockers |
| Data & QA review | `.project/agents/data_qa_auditor.md` | Verify analytics reuse the clinical core and introduce no new thresholds |

**Acceptance:** full validation gate green (all tiers + trajectory); both reviewer subagents report no Blockers; docs updated; `SESSION_STATUS.md` reflects the feature complete.

**Effort:** small–medium. ~1 session.

---

## Sequencing & dependencies

```
T0 (data model) ──► T1 (analytics) ──► T2 (API) ──► T3 (frontend) ──► T4 (gate/review)
                         │
                         └─ reuses clinical/thresholds.py + biomarkers.py (no changes)
```

Strictly linear; each phase has a green-tests gate before the next. T1 is the highest-value/highest-care phase (analytics + safety). T3 is the largest by effort (UI). Total: roughly 6–8 focused sessions.

---

## Definition of done (the whole capability)

- [ ] User can enter multiple dated draws or import a health file.
- [ ] Per-biomarker timeline renders with category bands and the user's points.
- [ ] Trajectory summary reports direction, change, category transitions, and intervention observations — descriptively.
- [ ] Export produces a portable, user-owned health file; import restores it; local cache can be cleared.
- [ ] Server stores nothing; `/api/v1/trajectory` is stateless.
- [ ] No predictive, causal, or risk-score language anywhere (enforced by tests + gate scan).
- [ ] `cohort_label` Literal and `disclaimer` present on every trajectory response; limitations always visible.
- [ ] New thresholds introduced: zero (clinical core reused).
- [ ] Full validation gate green; Clinical & Safety + Data & QA reviewers: no Blockers.
- [ ] `ARCHITECTURE.md`, `SAFETY_AND_LIMITATIONS.md`, `RELEASE_CHECKLIST.md`, `SESSION_STATUS.md` updated.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Trajectory features drift into prediction/advice | Hard guardrails in code + dedicated guardrail tests + gate scan + reviewer pass; "descriptive-only" is a definition-of-done item |
| Small-N trends mislead users | Mandatory "few draws can mislead" limitation on every timeline view; "insufficient_data" direction when <2 points; no projection |
| Privacy posture erodes if storage creeps in | Architectural decision recorded: user-owned file only, server stateless; accounts explicitly deferred to a gated phase |
| Duplicating clinical logic | Analytics reuse `classify_all_biomarkers`; Data & QA Auditor checks for zero new thresholds |
| Contract drift (API vs frontend) | `types.ts` mirrored in the same change; `npm run type-check` in the gate |
| Still partially replicable by a chatbot | Accepted and documented (spec §10); moat is the *combination* — verified logic + real percentiles + portable artifact + privacy — and the plan keeps raising the rigor bar |

---

## What this unlocks next (future, post-capability)

Not part of this build, but the natural follow-ons once trajectory exists:
- **Guideline-version tracking** — record which guideline version classified each draw, so historical points stay accurate as guidelines evolve. Deepens the "verifiable" moat.
- **Expanded verified biomarker set** (e.g. ApoB, Lp(a)) — each added with the same single-source-of-truth + test discipline.
- **Clinician-shareable export** — a clean PDF of the timeline for an appointment (builds on the existing PDF capability).
- **Server-side accounts** — only behind a full HIPAA/security review, and only if user demand justifies trading away the statelessness advantage.
