# SAHC RiskLens — Documentation Index

Start here. SAHC RiskLens is an educational, non-diagnostic web app for
understanding cardiometabolic lab values with South Asian risk context. The
project root [`README.md`](../README.md) has the quick start.

## Read by goal

**Understand the product**
- [`PRODUCT_DESCRIPTION.md`](PRODUCT_DESCRIPTION.md) — what it is, who it's for, how it improves on SCORE
- [`PRODUCT_OVERVIEW.md`](PRODUCT_OVERVIEW.md) — personas, user stories, success measures
- [`PRD.md`](PRD.md) — product requirements + roadmap

**Understand the build**
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system design (three tiers, data flow, invariants)
- [`API_REFERENCE.md`](API_REFERENCE.md) — endpoints, parameters, request/response schemas
- [`FEATURES.md`](FEATURES.md) — feature-by-feature guide with code pointers
- [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) — setup, run, test, conventions, how to extend

**Clinical & data**
- [`CLINICAL_LOGIC_APPENDIX.md`](CLINICAL_LOGIC_APPENDIX.md) — every threshold + citation (source of truth)
- [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) — NHANES variables and real-data gotchas
- [`SAHC_COHORT.md`](SAHC_COHORT.md) — SAHC cohort provenance, peer matching, governance
- [`CLINICIAN_BRIEFING.md`](CLINICIAN_BRIEFING.md) — the physician-review framing and safety posture
- [`SAHC_RiskLens_Clinician_Briefing.docx`](SAHC_RiskLens_Clinician_Briefing.docx) — clinician-facing briefing (Word)

**Safety, validation, release**
- [`SAFETY_AND_LIMITATIONS.md`](SAFETY_AND_LIMITATIONS.md) — boundaries and known limits
- [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) · [`E2E_CHECKLIST.md`](E2E_CHECKLIST.md) · [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)
- [`DEPLOYMENT.md`](DEPLOYMENT.md) — single-container deployment
- [`PHASE2_ROADMAP.md`](PHASE2_ROADMAP.md) — what gates production use
- [`INCREMENTAL_VALUE_SPEC.md`](INCREMENTAL_VALUE_SPEC.md) — the differentiation thesis
- [`SESSION_STATUS.md`](SESSION_STATUS.md) — living status + decision log
- [`PR_feat_sahc_cohort.md`](PR_feat_sahc_cohort.md) — PR description for the cohort/matching/markers work

## The non-negotiables (every contributor)

1. Descriptive, never diagnostic — no diagnosis, prediction, or treatment advice.
2. Honest cohort labels — the NHANES cohort is never called "South Asian".
3. One source of truth for thresholds; the frontend renders what the API returns.
4. `results.py` ↔ `types.ts` change together.
5. Stateless server; raw patient rows are never committed.
6. `bash scripts/run_validation_gate.sh` must pass before any release.

## Current state

Phase 1 — educational demonstration. Implemented: guideline classification,
dual-cohort benchmarking (NHANES + SAHC), SCORE-style peer matching, ApoB/Lp(a)
risk-enhancing markers, South Asian context, longitudinal trajectory, physician
guide + clinician pre-visit brief + care navigation. **294 backend tests pass;
the validation gate passes.** Pending clinician sign-off: the ApoB/Lp(a)
thresholds and the SAHC cohort. Data-blocked follow-ups (response-to-intervention,
velocity benchmarking) require a linked, date-stamped extract — see
[`SAHC_COHORT.md`](SAHC_COHORT.md) and [`PR_feat_sahc_cohort.md`](PR_feat_sahc_cohort.md).
