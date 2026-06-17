# PRD — Trajectory Tracking, Phases T0–T1 (Clinical Core)

> Scope of this PRD: the **framework-free clinical core** for longitudinal tracking — the data model (T0) and the descriptive analytics engine (T1). The API endpoint (T2) and frontend (T3) are separate PRDs. Parent context: `docs/INCREMENTAL_VALUE_SPEC.md`.

## 1. Problem & objective
A single lab snapshot is commoditized; the durable clinical signal is in the *trajectory* of values over time. T0–T1 deliver the engine that turns an ordered set of dated lab draws into descriptive trajectory analytics, reusing the existing verified clinical thresholds and introducing **zero** new clinical logic.

## 2. Users (for this slice)
- **Downstream engineer (T2/T3)** — consumes `analyze_series()` to build the API and UI. Needs a stable, typed, JSON-friendly contract.
- **Clinical & Safety Reviewer** — must be able to confirm output is descriptive, not predictive.
- **Data & QA Auditor** — must confirm the engine reuses the clinical core and adds no thresholds.

## 3. Functional requirements
- **FR1** Represent a dated draw (`draw_date` + the existing 16-field panel + optional label).
- **FR2** Represent an ordered series of draws; normalize by sorting ascending by date; reject an empty series; reject future-dated draws.
- **FR3** Export a series to a portable, user-owned "health file" (dict/JSON) and import it back, round-trip lossless, with schema versioning.
- **FR4** Per biomarker, compute: ordered points (date, value, category, tone), direction, absolute change, per-year rate of change, and category transitions.
- **FR5** Detect interventions: a medication flag flipping false→true between consecutive draws, with the descriptively-stated observed effect on the affected biomarkers.
- **FR6** Per-point categories MUST come from the existing `classify_all_biomarkers`. The medication→biomarker mapping MUST come from the existing clinical modules (no redefinition).

## 4. Non-functional requirements
- **NFR1 (framework-free)** The core imports no web framework and no API models. Plain dataclasses only.
- **NFR2 (single source of truth)** No new thresholds; no duplicated medication map.
- **NFR3 (descriptive-only safety)** No predictive, causal, or risk-score language in any output. Enforced by tests.
- **NFR4 (determinism)** Same input → same output; arithmetic is transparent (no opaque model).
- **NFR5 (TDD)** Every requirement has a failing test written before its implementation.

## 5. Out of scope (T0–T1)
API endpoint/router, Pydantic request models, frontend, persistence beyond the in-memory health-file dict, any forward projection.

## 6. Acceptance criteria
- All FR/NFR covered by tests in `tests/test_series.py` and `tests/test_trajectory_analytics.py`, all green.
- Full pre-existing suite (184 tests) still green after additive changes.
- Clinical & Safety Reviewer and Data & QA Auditor personas: no Blockers.

## 7. Direction semantics (clinical reference for FR4)
"Improving" means movement toward the guideline-preferred direction. Lower is preferred for LDL, TG, TC, HbA1c, FPG, SBP, DBP, BMI. Higher is preferred for HDL. This is the only biomarker-specific judgment in the engine and is documented in the design doc; it is not a new threshold.
