# Add South Asian cohort, SCORE-style peer matching, and advanced-marker / clinician-brief layers

`feat/sahc-cohort` → `main`

## Summary

This branch closes the capability gap between RiskLens and the original SCORE
tool, and then extends past it — while keeping every existing safety and
labeling invariant intact. It lands in three coherent batches:

1. **A genuine South Asian benchmark cohort** (selectable alongside NHANES).
2. **SCORE-style peer matching** (sex / age / medication), with small-cell
   suppression and transparent fallback — an improvement over SCORE, not just
   parity.
3. **Ship-now value layers that need no new data:** ApoB / Lp(a) risk-enhancing
   markers, a clinician pre-visit brief, and care-navigation prompts.

Default behavior is unchanged (NHANES cohort, no matching), so all prior
contracts and tests hold. **294 backend tests pass (13 skipped), frontend
type-check is clean, and the validation gate passes.**

---

## What changed, by batch

### 1. South Asian Heart Center cohort (`952e7ad`)
- Added the SAHC clinical cohort (de-identified South Asian patients) as a
  **second, separately-labeled, opt-in** benchmark — the real South Asian
  population the product's thesis said was missing (NHANES NH-Asian is only a
  proxy).
- `?cohort=sahc` on `POST /api/v1/benchmark`; a "Compare against" selector in the
  UI; `cohort` + widened `cohort_label` on the response.
- Live computation from the raw CSV when present, else a frozen aggregate table
  (verified identical). Raw patient rows are **never committed** (gitignored);
  only aggregate percentiles are tracked.
- **Labeling invariant enforced by tests:** the NHANES cohort is never called
  "South Asian"; the SAHC cohort carries its own proper-noun label.

### 2. Peer matching (`deaac2b`)
- `?match=true` benchmarks each value against the patient's matched subgroup
  (sex + age band + medication use), like SCORE's peer matching. Requires age +
  sex.
- **Better than SCORE:** suppresses peer cells below 30 people (SCORE computed on
  any cell, however small), falls back transparently (full → sex+age → whole
  cohort), and discloses the peer group used (`match_description`) and its size
  (`match_n`) on every point.
- Frozen, aggregate-only stratified table for demo mode; live computation when
  the raw cohort is present (verified equal).
- Offered for the SAHC cohort; NHANES falls back to whole-cohort with disclosure
  (too small to stratify reliably, and raw files not shipped).

### 3. Advanced markers + brief + navigation (this batch — pending commit)
- **ApoB / Lp(a) as classification-only risk-enhancing markers.** Not part of the
  benchmarked core 9 (no cohort measures them); classified against 2018 AHA/ACC
  risk-enhancer thresholds. Blank markers are omitted (never flagged "missing").
  ApoB carries a statin medication note; elevated Lp(a) adds a South Asian
  context item. **Thresholds marked PENDING CLINICAL REVIEW** in the appendix.
- **Clinician pre-visit brief.** A frontend-only, copy-to-clipboard summary
  compiled from the existing response (out-of-range values + guideline sources,
  advanced markers, matched-peer context, medications, discussion topics, missing
  data). No new API surface.
- **Care navigation.** Two non-prescriptive prompts — family / cascade screening
  (triggered by South Asian ancestry or elevated heritable Lp(a)) and a pointer
  to the center's existing prevention program (routes to vetted content rather
  than generating advice). Language scanned to stay non-diagnostic.

---

## Safety & boundaries (unchanged)
- No diagnosis, prediction, or treatment advice; disclaimers always rendered.
- Classification is guideline-based and cohort-independent — selecting a cohort or
  matching changes only the comparison distribution, never the clinical category.
- Server remains stateless; no patient rows added to the repo.
- New thresholds (ApoB/Lp(a)) flagged for clinician sign-off, consistent with the
  project's "propose, clinician verifies" model.

## Data provenance / governance
- SAHC cohort provenance, method, and caveats documented in `docs/SAHC_COHORT.md`.
- Known caveats surfaced honestly: SAHC fasting glucose includes non-fasting
  draws (no fasting field in the extract); BP is a single reading; ApoB/Lp(a) are
  classified, not benchmarked. External use of SAHC aggregates is gated on the
  center's data-use terms.

## Testing
- `python -m pytest tests/ --ignore=tests/browser` → 294 passed, 13 skipped.
- New suites: `test_sahc_cohort.py`, `test_peer_matching.py`,
  `test_risk_enhancing_markers.py`, `test_care_navigation.py`.
- `cd frontend && npm run type-check` → clean (contract mirrored in `types.ts`).
- `bash scripts/run_validation_gate.sh` → **Validation gate PASSED**.

## Follow-ups (not in this PR)
- The high-value longitudinal layers (response-to-intervention, velocity
  benchmarking) are **blocked on data**: the de-identified extract is
  cross-sectional with no patient linkage. Unblocking them requires a governed,
  pseudonymously-linked, date-stamped extract from the center — tracked
  separately.
- NHANES peer matching and ApoB/Lp(a) benchmarking depend on richer source data.
