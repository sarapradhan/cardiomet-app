# Build Log — Trajectory Tracking, Phases T0–T1

Record of the TDD cycle and persona reviews for the longitudinal trajectory
clinical core. Methodology: design-first, test-first (red→green), then
independent persona review — as in a software engineering organization.

## Methodology
1. PRD written (`docs/trajectory/PRD_TRAJECTORY_T0_T1.md`).
2. Technical design written (`docs/trajectory/DESIGN_TRAJECTORY_T0_T1.md`).
3. TDD per phase: tests written first, run to confirm RED, implement to GREEN.
4. Full regression after additive changes to shared modules.
5. Three persona reviews against the design's review gates.

## TDD cycle

### T0 — data model
- Wrote `tests/test_series.py` (12 tests) FIRST.
- RED: `ModuleNotFoundError: No module named 'sahc_risklens.trajectory'`.
- Implemented `trajectory/__init__.py`, `series.py`, `health_file.py`.
- GREEN: 12/12 passed.

### T1 — analytics engine
- Wrote `tests/test_trajectory_analytics.py` (24 tests) FIRST.
- RED: `ModuleNotFoundError: ...trajectory.analytics`.
- Added additive public accessors to the clinical core so the medication map is
  reused, not duplicated: `thresholds.medication_affects()`,
  `disclaimers.medication_labels()`.
- Implemented `trajectory/analytics.py`.
- GREEN: 24/24 passed on first implementation run.

### Full regression
- 220 tests pass (184 pre-existing + 36 new). Zero regressions from the
  additive accessor changes.

## Persona reviews

### Staff Engineer — Architecture & Code Review — PASS
- Framework-free: trajectory/ imports only stdlib + the clinical core; no
  fastapi/pydantic/api imports. ✓
- Contracts are immutable: 7 frozen dataclasses. ✓
- Each module exposes a deliberate `__all__`. ✓
- Reuse is correct: categories via `classify_all_biomarkers`, units via
  `BIOMARKERS`, medication map via `medication_affects()`. ✓

### Data & QA Auditor — PASS
- Zero new clinical thresholds; all categorization delegated to the clinical
  core. ✓
- Medication→biomarker map reused, not redefined. ✓
- Deadband documented explicitly as a display-noise threshold, not clinical
  significance. ✓
- Drift guard: all 19 categories the classifier can emit map to a known tone. ✓
- 36 tests cover the new modules. ✓

### Clinical & Safety Reviewer — PASS (1 false-positive noted, no Blockers)
- Source scan flagged one line — the docstring that *describes* the
  descriptive-only rule ("emits no predictive or causal language"). Confirmed
  false positive: it is a self-referential comment, not output.
- Decisive check: scanned actual runtime output strings across a multi-scenario
  series (med starts, transitions, both directions) — zero forbidden tokens
  (will/predict/forecast/risk/lowered/caused/because/recommend/diagnose/…). ✓
- Intervention phrasing is observational ("LDL changed from 162 to 124
  (decreased 38 mg/dL) by the next draw"), never causal. ✓
- `direction` is a neutral enum describing the number's movement vs. the
  guideline-preferred direction, not the person. ✓
- Future-dated draws rejected at ingest, so no output can be future-dated. ✓

## Outcome
T0–T1 complete. Clinical core for longitudinal tracking implemented, fully
tested (36 new tests, 220 total green), and cleared by all three persona
reviews with no Blockers. Ready for T2 (stateless API endpoint).
