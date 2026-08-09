# SAHC RiskLens — Architecture

> **Responsible cardiometabolic benchmarking for South Asian heart health.**
> Educational only. Not a diagnostic tool, not a medical device, not a substitute
> for clinical judgment.

This is the authoritative description of how the system is built and why, current
as of the cohort-selection, peer-matching, and advanced-marker work. For product
scope see [`PRODUCT_DESCRIPTION.md`](PRODUCT_DESCRIPTION.md) and [`PRD.md`](PRD.md);
for exact clinical values see [`CLINICAL_LOGIC_APPENDIX.md`](CLINICAL_LOGIC_APPENDIX.md);
for NHANES variables see [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md); for the SAHC
cohort and peer matching see [`SAHC_COHORT.md`](SAHC_COHORT.md); for the HTTP
surface see [`API_REFERENCE.md`](API_REFERENCE.md).

---

## 1. What this system does

A user enters cardiometabolic lab values and vitals (lipids, glucose, HbA1c,
blood pressure, BMI), optionally advanced lipids (ApoB, Lp(a)), plus demographics
and medication flags. The system returns several layers of context:

1. **Clinical threshold classification** — each value placed in a guideline
   category (e.g. LDL "High", HbA1c "Prediabetes"), sourced from ACC/AHA, ADA,
   NCEP, WHO.
2. **Population benchmark** — the value positioned (p10–p90) against a
   **selectable reference cohort**: NHANES Non-Hispanic Asian (default proxy) or
   the South Asian Heart Center clinical cohort (genuine South Asian population).
3. **Peer matching (optional)** — the benchmark narrowed to the patient's matched
   subgroup (sex + age band + medication use), with small-cell suppression.
4. **Advanced lipid markers** — ApoB and Lp(a), classified as guideline risk-
   enhancing factors (classification-only; no cohort percentile).
5. **South Asian risk context** — qualitative, guideline-backed discussion points,
   shown when the user reports South Asian ancestry (or for elevated Lp(a)).
6. **Physician guide, pre-visit brief, and care navigation** — template prompts,
   a clinician summary, and non-prescriptive next-step pointers.
7. **Longitudinal trajectory** — descriptive trends across dated draws, with the
   data owned by the user and nothing stored server-side.

Everything is framed for discussion, never diagnosis. Safety guarantees are
enforced by the type system and tests: each benchmark cohort carries its own
honest label (the NHANES cohort is never called "South Asian"), and a disclaimer
is always present in every response.

---

## 2. Guiding architectural principles

In priority order; the higher wins on conflict.

1. **Medical safety is structural, not procedural.** Invariants live where they
   cannot be forgotten: `disclaimer` is a required min-length field; `cohort_label`
   is a constrained `Literal` union; the limitations panel renders unconditionally.
2. **One source of truth per fact.** Thresholds live only in `thresholds.py`
   (mirrored to the appendix); NHANES variables only in the dictionary + loader;
   the API contract only in `results.py` (mirrored to `types.ts`).
3. **Clinical logic is framework-free.** All rules live in `sahc_risklens/`, which
   imports no web framework. Routers are thin adapters.
4. **Demo and live are output-identical.** Frozen aggregate tables (cohort
   percentiles and stratified peer tables) are verified equal to the live
   computation, so toggling data presence never changes what a user sees.
5. **The frontend never does clinical work.** It renders exactly what the API
   returns — disclaimer, cohort label, and categories verbatim.

---

## 3. System topology

```
                          Browser
                             │
                   ┌─────────▼──────────┐
                   │  Next.js 14 (App   │   static export, co-hosted with the
                   │  Router) UI        │   API in one container (or split)
                   └─────────┬──────────┘
                             │  HTTPS
                             │   POST /api/v1/benchmark?cohort=&match=
                             │   POST /api/v1/trajectory
                             │   GET  /api/v1/thresholds   GET /health
                   ┌─────────▼──────────┐
                   │   FastAPI (api/)   │   thin routers; validate + delegate
                   └─────────┬──────────┘
                             │  in-process function calls
                   ┌─────────▼───────────────────────────────┐
                   │   sahc_risklens/  (pure Python)          │
                   │   clinical/   thresholds, biomarkers,    │
                   │               SA context, disclaimers,   │
                   │               care navigation            │
                   │   data/       NHANES + SAHC loaders,     │
                   │               filters, frozen tables     │
                   │   benchmark/  percentile + peer matching │
                   │   trajectory/ series, health file,       │
                   │               descriptive analytics      │
                   └─────────┬───────────────────────────────┘
                             │ (live mode only)
                   ┌─────────▼─────────────────────────┐
                   │  NHANES XPT files / SAHC CSV       │  absent in demo;
                   │  (gitignored, local)              │  frozen tables used
                   └────────────────────────────────────┘
```

The system is **stateless**: no patient value is persisted server-side. Results
live only in the browser's `sessionStorage`; longitudinal history is a
user-exported health file. This minimizes the privacy/regulatory surface (§9).

---

## 4. The three tiers in detail

### 4.1 Clinical core — `sahc_risklens/` (framework-free Python)

| Module | Responsibility |
|---|---|
| `config.py` | Canonical constants; `NHANES_COHORT_LABEL`, `SAHC_COHORT_LABEL`, `COHORT_*` ids, `COHORT_LABELS`, `cohort_label()`; demo/live detection; data paths |
| `clinical/biomarkers.py` | Registry mapping input fields → output labels/units; the canonical 9-biomarker set; missing-biomarker detection |
| `clinical/thresholds.py` | Threshold classification engine (core 9) **and** the advanced risk-enhancing markers (ApoB, Lp(a)); every cut-point mirrored to the appendix |
| `clinical/south_asian_context.py` | Qualitative SA context items (ancestry, BMI, elevated Lp(a)); never quantifies risk |
| `clinical/care_navigation.py` | Non-prescriptive next-steps: family/cascade screening, prevention-program pointer |
| `clinical/disclaimers.py` | Template physician guide + medication notes — **no LLM** |
| `data/nhanes_loader.py` | Reads XPT, joins on `SEQN`, applies cohort + fasting filters, BP means, renames to internal keys |
| `data/sahc_cohort_loader.py` | Reads the SAHC CSV; biomarker frame and matching frame (sex/age band/meds) |
| `data/cohort_filters.py` | `RIDRETH3` cohort filter; `PHAFSTHR >= 8` fasting filter |
| `data/missingness.py` | Reports missing values; never imputes |
| `data/demo_cohort.py` / `sahc_demo_cohort.py` | Frozen real percentiles for each cohort (demo mode) |
| `data/strata_tables.py` (+ `.json`) | Frozen, aggregate-only stratified percentiles for peer matching |
| `benchmark/percentile.py` | Resolves data source (live vs frozen) per cohort; whole-cohort + matched benchmark points; percentile rank |
| `benchmark/matching.py` | Peer-matching helpers + stratified computation (live frame and frozen table); suppression + fallback |
| `trajectory/series.py` | Dated-draw/series model + validation (no future dates), sorting, immutability |
| `trajectory/health_file.py` | Portable user-owned export/import (no server storage) |
| `trajectory/analytics.py` | Descriptive longitudinal analytics; reuses the classifier; zero new thresholds |

**Classification algorithm.** Each table is an ascending list of
`(lower_bound_inclusive, category, range_description)`; a value classifies to the
last entry whose lower bound it meets. HbA1c/FPG prediabetes upper bounds are
exclusive (6.49 is Prediabetes); HDL branches on sex. BMI is dual: the standard
WHO category appears in `threshold_results`; the South Asian category (23 / 27.5)
is produced separately for the context panel only.

**Benchmark engine.** `get_cohort_percentiles(cohort)` returns p10/p25/median/
p75/p90 + n for a cohort, from live data when present else the frozen table
(verified identical). `get_benchmark_data(data, cohort, match)` builds
`BenchmarkPoint`s; with `match=True` it calls `get_matched_percentiles`, which
selects the narrowest reliable peer stratum (sex+age+meds → sex+age → whole
cohort), suppresses cells below `MIN_COHORT_N` (30), and records the matched n and
a plain-language peer description. Advanced markers are classified by
`classify_risk_enhancing_markers` and are deliberately *not* benchmarked.

### 4.2 API tier — `api/` (FastAPI, thin)

| File | Role |
|---|---|
| `api/main.py` | App construction, CORS, router registration, single-container static serving |
| `api/models/patient.py` | `BiomarkerInput` — validated input (incl. optional `ApoB_mgdl`, `Lpa_mgdl`) |
| `api/models/results.py` | **Authoritative output contract.** `BenchmarkResponse` and parts; `CohortLabel` union; matching + `risk_enhancing_markers` + `care_navigation` fields |
| `api/routers/benchmark.py` | `POST /api/v1/benchmark` — orchestrates the core; validates `?cohort=` and `?match=` |
| `api/routers/thresholds.py` | `GET /api/v1/thresholds` — reference table |
| `api/routers/health.py` | `GET /health` — liveness + demo/live indicator |
| `api/models/series.py`, `api/models/trajectory.py`, `api/routers/trajectory.py` | Dated-series input and stateless trajectory endpoint |

Routers hold no clinical logic or NHANES variable names. The two pieces of
orchestration they own: gating the South Asian context (only when `south_asian`),
and validating/passing the `cohort` and `match` selectors.

### 4.3 Presentation tier — `frontend/` (Next.js 14 + TypeScript)

| Path | Role |
|---|---|
| `src/app/layout.tsx` | Always-visible disclaimer, nav, attribution |
| `src/app/benchmark/page.tsx` | Input flow; **cohort selector** + **"Match to people like me"** toggle; posts to API |
| `src/app/results/page.tsx` | Renders results in order; disclaimer first, limitations last |
| `src/app/timeline/page.tsx` | Multi-draw entry, analyze, export/import |
| `src/components/ThresholdCards.tsx` | Per-biomarker classification cards |
| `src/components/RiskEnhancingMarkers.tsx` | ApoB/Lp(a) cards (classification-only) |
| `src/components/DistributionChart.tsx` | Percentile-band chart with the patient marker |
| `src/components/SouthAsianContextPanel.tsx` | SA context, verbatim |
| `src/components/CareNavigation.tsx` | Family-screening / prevention pointers |
| `src/components/ClinicianBrief.tsx` | Copy-to-clipboard pre-visit summary (compiled client-side) |
| `src/components/PhysicianGuide.tsx`, `MedicationNotes.tsx`, `LimitationsPanel.tsx`, `Timeline.tsx`, `TrajectorySummary.tsx` | Discussion prompts, caveats, structural limitations, longitudinal views |
| `src/lib/types.ts` | TypeScript mirror of `results.py` (the contract's other half) |
| `src/lib/api.ts` | API client; `submitBiomarkers(input, cohort, match)`; reads `NEXT_PUBLIC_API_URL` |
| `src/lib/categoryStyles.ts`, `biomarkerMeta.ts` | Presentation only |

---

## 5. The request lifecycle

1. **Browser** — `BiomarkerForm` builds a typed `BiomarkerInput`; the page also
   holds the selected `cohort` and `match` flag; `api.ts` POSTs to
   `/api/v1/benchmark?cohort=&match=`.
2. **Validation** — FastAPI validates `BiomarkerInput`; an unknown `cohort` → 422.
3. **Orchestration** — `benchmark.py` calls: `classify_all_biomarkers` →
   `classify_risk_enhancing_markers` → `get_benchmark_data(data, cohort, match)`
   → `find_missing_biomarkers` → `get_medication_notes` → `build_physician_guide`
   → `get_south_asian_context` (if `south_asian`) → `get_care_navigation`.
4. **Assembly** — a `BenchmarkResponse`; `cohort_label`, `disclaimer`, and the
   matching/markers/navigation fields are populated; defaults guarantee the
   safety fields are present.
5. **Render** — the frontend stores the response and renders: disclaimer →
   badges (cohort + matched peers) → threshold cards → risk-enhancing markers →
   distribution → SA context → medication notes → physician guide → care
   navigation → clinician brief → limitations.

The **longitudinal flow** posts a dated series to the stateless
`POST /api/v1/trajectory`; the server computes and returns, storing nothing.

---

## 6. The data pipelines

**NHANES (default cohort).** 2017–2018 public XPT files (`_J`): join on `SEQN`,
filter `RIDRETH3 == 6` (Non-Hispanic Asian), compute BP means, apply the
`PHAFSTHR >= 8` fasting filter to glucose, rename to internal keys, compute
percentiles. Frozen to `demo_cohort.py` for demo mode. (Two real-data
corrections are documented in the dictionary: auscultatory BP variable names,
and fasting duration living in `FASTQX_J`.)

**SAHC (opt-in cohort).** De-identified clinic CSV at `data/sahc/` (gitignored):
filter `RIDRETH3 == 1` (South Asian), rename to internal keys, compute
percentiles; frozen to `sahc_demo_cohort.py`. Stratified peer tables (sex × age ×
medication, suppressed below 30) frozen to `strata_tables.json` via
`scripts/build_strata_tables.py`. Documented caveats: glucose has no fasting
field; BP is a single reading. See [`SAHC_COHORT.md`](SAHC_COHORT.md).

**Advanced markers.** ApoB and Lp(a) are *not* in either cohort, so they are
classification-only (no percentile) — see [`CLINICAL_LOGIC_APPENDIX.md`](CLINICAL_LOGIC_APPENDIX.md).

---

## 7. The data contract and how it stays in sync

The output shape is defined once in `api/models/results.py` and mirrored in
`frontend/src/lib/types.ts`. Rule: **change them in the same commit**;
`npm run type-check` fails otherwise. `BenchmarkResponse` fields:
`threshold_results`, `risk_enhancing_markers`, `benchmark_data` (each
`BenchmarkPoint` carries `matched`/`match_n`/`match_description`),
`south_asian_context`, `physician_guide`, `care_navigation`, `missing_biomarkers`,
`medication_notes`, `cohort`, `cohort_label`, `matched`, `match_description`,
`disclaimer`, `validation_status`.

---

## 8. Testing architecture

**307 backend tests** (plus a 23-test browser tier), run in order by the validation gate:

| Tier | Representative files | Proves |
|---|---|---|
| Smoke | `test_smoke.py` | Every module imports; entry points run on minimal input |
| Unit | `test_thresholds.py`, `test_percentile.py`, `test_sahc_cohort.py`, `test_peer_matching.py`, `test_risk_enhancing_markers.py`, `test_care_navigation.py`, `test_cohort_filters.py`, `test_missingness.py`, `test_series.py`, `test_trajectory_analytics.py`, `test_biomarker_mapping.py` | Each function correct in isolation: thresholds at every boundary; cohort + peer-matching correctness, suppression/fallback, and the no-crossed-labels invariant; advanced-marker classification; care-navigation language safety; trajectory analytics |
| Integration | `test_api_endpoints.py`, `test_integration.py`, `test_trajectory_api.py` | Components agree through the API; cohort/match/markers/navigation round-trip |
| E2E | `test_e2e.py` | Real server over HTTP: contract, safety invariants, CORS, validation |

`bash scripts/run_validation_gate.sh` is the single pre-release command: all test
tiers + TypeScript type-check + required-docs check + diagnostic-language scan +
structural checks (cohort filter, HbA1c, BP vars, fasting filter, trajectory
descriptive-only). Real-data tests skip cleanly when files are absent.

---

## 9. Safety, privacy, and the demo/production boundary

**Statelessness.** No patient value is stored, logged, or persisted server-side.

**Enforced invariants** (tested):
- `disclaimer` is required (min length) and rendered first.
- `cohort_label` is a constrained union; the NHANES cohort is never labeled
  "South Asian" and the SAHC cohort never inherits the NHANES label
  (`test_sahc_cohort.py`).
- The limitations panel renders unconditionally.
- No LLM in the patient-facing path; physician guide and care navigation are
  fixed templates; their language is scanned for diagnostic/predictive phrasing.
- Peer matching suppresses unreliable small cells and discloses the matched n.
- Medication flags surface a note but never alter a classification.

**Production readiness.** This is a complete, tested, demo-ready educational tool.
Moving beyond a demo is gated on documented clinician review (including the
ApoB/Lp(a) thresholds and SAHC cohort), a non-device CDS determination, a privacy
policy, security hardening, and accessibility.

---

## 10. Technology stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript (strict), static export |
| Backend | FastAPI, Pydantic v2, Uvicorn |
| Clinical core | Python ≥3.11, pandas, numpy |
| Data | NHANES XPT + SAHC CSV (live) or frozen aggregate tables (demo) |
| Tests | pytest, httpx TestClient, real-server e2e, Playwright (browser tier) |

---

## 11. Deployment

Single container: the Dockerfile builds the static frontend (Node) and serves it
from FastAPI (Python) on `$PORT` (7860 default for Hugging Face Spaces). Config
via `NEXT_PUBLIC_API_URL` and `ALLOWED_ORIGINS`. See [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## 12. Repository map

```
cardiomet-app/
├── README.md · CLAUDE.md · CONTRIBUTING.md · docker-compose.yml · Dockerfile
├── sahc_risklens/            # clinical core (framework-free)
│   ├── config.py
│   ├── clinical/   biomarkers, thresholds, south_asian_context,
│   │               care_navigation, disclaimers
│   ├── data/       nhanes_loader, sahc_cohort_loader, cohort_filters,
│   │               missingness, demo_cohort, sahc_demo_cohort,
│   │               strata_tables(.py/.json)
│   ├── benchmark/  percentile, matching
│   └── trajectory/ series, health_file, analytics
├── api/
│   ├── main.py
│   ├── models/     patient, results, series, trajectory
│   └── routers/    benchmark, thresholds, health, trajectory
├── frontend/src/
│   ├── app/        layout, page, benchmark, results, timeline
│   ├── components/ ThresholdCards, RiskEnhancingMarkers, DistributionChart,
│   │               SouthAsianContextPanel, CareNavigation, ClinicianBrief,
│   │               PhysicianGuide, MedicationNotes, LimitationsPanel,
│   │               Timeline, TrajectorySummary, BiomarkerForm, NavBar, …
│   └── lib/        types, api, categoryStyles, biomarkerMeta, healthFile
├── tests/          smoke → unit → integration → e2e (+ tests/browser)
├── scripts/        setup_env.sh, download_nhanes.py, build_strata_tables.py,
│                   run_validation_gate.sh
├── data/           raw/ (NHANES XPT, gitignored) · sahc/ (CSV, gitignored)
└── docs/           this file + the documents linked at the top
```

---

## 13. Extending the system safely

- **Threshold change** → edit `CLINICAL_LOGIC_APPENDIX.md` and `thresholds.py`
  together, add boundary tests, run the gate.
- **New cohort** → add a loader + frozen table + a `COHORT_*` id/label; keep the
  no-crossed-labels invariant; extend `test_sahc_cohort.py`.
- **New benchmark dimension (e.g. matching axis)** → extend `matching.py`,
  regenerate the frozen strata table, suppress small cells.
- **API response change** → update `results.py` and `types.ts` in the same change.
- **Any clinical/UI copy** → re-run the diagnostic-language scan; clinician review
  before release.
- **Before any release** → `bash scripts/run_validation_gate.sh` must pass.
