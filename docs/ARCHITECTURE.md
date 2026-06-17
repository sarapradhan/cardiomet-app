# SAHC RiskLens — Architecture

> **Responsible cardiometabolic benchmarking for South Asian heart health.**
> Educational only. Not a diagnostic tool, not a medical device, not a substitute for clinical judgment.

This document is the authoritative description of how the system is built and why. It is written for an engineer or reviewer who needs to understand the whole system quickly, extend it safely, or audit its clinical and data-handling claims. For product scope see `docs/PRD.md`; for the exact clinical values see `docs/CLINICAL_LOGIC_APPENDIX.md`; for NHANES variables see `docs/DATA_DICTIONARY.md`.

---

## 1. What this system does

A user enters cardiometabolic lab values and vitals (lipids, glucose, HbA1c, blood pressure, BMI) plus a few demographics and medication flags. The system returns four layers of context:

1. **Clinical threshold classification** — each value placed into a guideline category (e.g. LDL "High", HbA1c "Prediabetes"), sourced from ACC/AHA, ADA, NCEP, and WHO.
2. **Population benchmark** — the value positioned against the NHANES Non-Hispanic Asian reference distribution (p10–p90), accurately labeled.
3. **South Asian risk context** — guideline-backed, qualitative discussion points (e.g. ancestry as a risk-enhancing factor; lower BMI cut-points), shown only when the user reports South Asian ancestry.
4. **Physician discussion guide** — template-generated prompts the user can raise with their clinician.

Everything is framed for discussion, never diagnosis. Two safety guarantees are enforced by the type system and tests: the cohort is always labeled exactly `"NHANES Non-Hispanic Asian"`, and a disclaimer is always present in every response.

---

## 2. Guiding architectural principles

The design follows five principles, in priority order. When they conflict, the higher one wins.

**1. Medical safety is structural, not procedural.** Safety guarantees are encoded where they cannot be forgotten: `cohort_label` is a Pydantic `Literal`, the `disclaimer` is a required field with a minimum length, and the limitations panel is rendered unconditionally in the UI. A developer cannot accidentally ship a response that omits them — the code will not compile or the tests will not pass.

**2. One source of truth per fact.** Every clinical threshold lives in exactly one place (`sahc_risklens/clinical/thresholds.py`, mirrored to `docs/CLINICAL_LOGIC_APPENDIX.md`). Every NHANES variable name lives in `docs/DATA_DICTIONARY.md` and the loader. The API contract lives in `api/models/results.py` and is mirrored to `frontend/src/lib/types.ts`. Divergence is treated as a bug.

**3. Clinical logic is framework-free.** All business rules live in the `sahc_risklens/` Python package, which imports no web framework. FastAPI routers are thin adapters: validate input, call the library, return the result. This keeps the clinical core testable in isolation and portable if the delivery layer ever changes.

**4. Demo and live must be indistinguishable in output.** The Phase 1 demo runs with no NHANES files by shipping the *real* Non-Hispanic Asian percentiles as a frozen table. The live path recomputes the same numbers from the raw files. They were verified identical across all nine biomarkers, so switching modes never changes what a user sees.

**5. The frontend never does clinical work.** No thresholds, no NHANES variable names, no risk logic in the browser. The frontend renders exactly what the API returns — including the disclaimer and cohort label, verbatim.

---

## 3. System topology

```
                          Browser
                             │
                   ┌─────────▼──────────┐
                   │  Next.js 14 (App    │   Vercel (or static export
                   │  Router) + MD3 UI   │   co-hosted with the API)
                   └─────────┬──────────┘
                             │  HTTPS  POST /api/v1/benchmark
                             │         GET  /api/v1/thresholds
                             │         GET  /health
                   ┌─────────▼──────────┐
                   │   FastAPI (api/)    │   Railway / Render / HF Space
                   │   thin routers      │
                   └─────────┬──────────┘
                             │  in-process function calls
                   ┌─────────▼──────────────────────────┐
                   │   sahc_risklens/  (pure Python)     │
                   │                                     │
                   │   clinical/    thresholds, schema,  │
                   │                context, guide       │
                   │   data/        NHANES loader,       │
                   │                filters, demo cohort │
                   │   benchmark/   percentile engine    │
                   └─────────┬──────────────────────────┘
                             │  (live mode only)
                   ┌─────────▼──────────┐
                   │  NHANES 2017–2018  │   read at startup; absent in
                   │  XPT files (local) │   demo mode (frozen table used)
                   └────────────────────┘
```

The system is **stateless**. No patient value is persisted server-side; results live only in the browser's `sessionStorage` for the current tab. This is a deliberate choice to minimize the privacy and regulatory surface (see §9).

---

## 4. The three tiers in detail

### 4.1 Clinical core — `sahc_risklens/` (framework-free Python)

This package is the heart of the system and the only place clinical decisions are made.

| Module | Responsibility | Key contract |
|---|---|---|
| `config.py` | Runtime configuration; the canonical `NHANES_COHORT_LABEL` and `PRODUCT_DISCLAIMER` strings; demo/live mode detection | Other modules import constants from here, never hardcode |
| `clinical/biomarkers.py` | Biomarker registry mapping API input fields (`LDL_mgdl`) to output labels (`LDL`), units, and full names; missing-biomarker detection | `BIOMARKERS` list is the canonical 9-biomarker set and order |
| `clinical/thresholds.py` | Threshold classification engine; every cut-point copied verbatim from the appendix | `classify_all_biomarkers()`, `classify_bmi_south_asian()`, `get_all_threshold_categories()` |
| `clinical/south_asian_context.py` | Guideline-backed qualitative South Asian context items | `get_south_asian_context(bmi_value)` — never quantifies risk |
| `clinical/disclaimers.py` | Template-based physician guide and medication notes — **no LLM** | `build_physician_guide()`, `get_medication_notes()` |
| `data/nhanes_loader.py` | Reads the real XPT files, joins on `SEQN`, applies cohort + fasting filters, computes BP means, renames to internal keys | `load_biomarker_frame()`, `nhanes_files_available()` |
| `data/cohort_filters.py` | `RIDRETH3 == 6` cohort filter; `PHAFSTHR >= 8` fasting filter | Raises loudly if `RIDRETH3` is missing rather than returning everyone |
| `data/missingness.py` | Reports missing values; never imputes or drops | `missingness_report()` |
| `data/demo_cohort.py` | Frozen real NH-Asian percentiles for the stateless demo | `get_demo_percentiles()` |
| `benchmark/percentile.py` | Resolves the data source (live vs demo) and produces benchmark points | `get_benchmark_data()`, `get_cohort_percentiles()` |

**The classification algorithm.** Each threshold table is an ascending list of `(lower_bound_inclusive, category, range_description)`. A value is classified to the *last* entry whose lower bound it meets or exceeds, so upper bounds are implicit (the next entry's lower bound). Two non-obvious cases are handled explicitly and tested: HbA1c/FPG prediabetes upper bounds are exclusive (an HbA1c of 6.49 is Prediabetes, not Diabetes), and HDL branches on sex (different tables for male and female).

**BMI is deliberately dual.** The standard WHO category appears in `threshold_results` (comparable to the NHANES benchmark). The South Asian category (cut-points 23 / 27.5) is produced *separately* by `classify_bmi_south_asian()` and surfaced only in the South Asian context panel — never presented as the NHANES benchmark. This separation prevents conflating a guideline discussion point with an empirical cohort statistic.

### 4.2 API tier — `api/` (FastAPI, thin)

| File | Role |
|---|---|
| `api/main.py` | App construction, CORS middleware (origins from `ALLOWED_ORIGINS`), router registration |
| `api/models/patient.py` | `BiomarkerInput` — Pydantic v2 input model with range validation (`ge`/`le`), sex pattern, optional fields |
| `api/models/results.py` | **The authoritative output contract.** `BenchmarkResponse` and its parts. `cohort_label: Literal["NHANES Non-Hispanic Asian"]` and `disclaimer: str = Field(min_length=20)` |
| `api/routers/benchmark.py` | `POST /api/v1/benchmark` — orchestrates the clinical core into a `BenchmarkResponse` |
| `api/routers/thresholds.py` | `GET /api/v1/thresholds` — returns the full reference table |
| `api/routers/health.py` | `GET /health` — liveness plus demo/live mode indicator |

Routers contain no clinical logic, no thresholds, and no NHANES variable names. They validate, delegate to `sahc_risklens/`, and assemble the response. The South Asian context is gated here (included only when `south_asian` is true), which is the one piece of orchestration the API owns.

### 4.3 Presentation tier — `frontend/` (Next.js 14 + Material Design 3)

| Path | Role |
|---|---|
| `src/app/layout.tsx` | Root layout: always-visible disclaimer banner, MD3 app bar, footer with cohort/guideline attribution |
| `src/app/page.tsx` | Landing page |
| `src/app/benchmark/page.tsx` | Input flow; posts to the API, stores result in `sessionStorage`, routes to results |
| `src/app/results/page.tsx` | Renders all result components in order; disclaimer first, limitations last (always) |
| `src/components/BiomarkerForm.tsx` | The input form; every clinical field optional |
| `src/components/ThresholdCards.tsx` | Per-biomarker classification cards; missing values shown as a muted chip, not omitted |
| `src/components/DistributionChart.tsx` | Percentile-band visualization with the patient's marker |
| `src/components/SouthAsianContextPanel.tsx` | Renders context items verbatim from the API |
| `src/components/MedicationNotes.tsx` | Medication caveats |
| `src/components/PhysicianGuide.tsx` | Discussion prompts |
| `src/components/LimitationsPanel.tsx` | Structural, always rendered, cannot be collapsed |
| `src/lib/types.ts` | TypeScript mirror of `api/models/results.py` — the contract's other half |
| `src/lib/api.ts` | API client; reads `NEXT_PUBLIC_API_URL`, never hardcodes URLs |
| `src/lib/categoryStyles.ts` | Maps a clinical category to a chip tone — presentation only, never alters the category |

The design system is Material Design 3, defined as CSS custom properties and a Tailwind token set in `globals.css` / `tailwind.config.js`: a clinical-blue primary, elevation shadows, a rounded shape scale, and four semantic chip tones (normal / elevated / high / missing). The aesthetic is intentionally restrained — in a medical context, credibility and legibility outrank flourish.

---

## 5. The request lifecycle

A single benchmark request flows through every tier:

1. **Browser** — `BiomarkerForm` collects input, builds a typed `BiomarkerInput`, and `api.ts` POSTs it to `/api/v1/benchmark`.
2. **Validation** — FastAPI validates against `BiomarkerInput`. Out-of-range values or a bad sex code are rejected with HTTP 422 before any logic runs.
3. **Orchestration** — `benchmark.py` calls, in sequence:
   - `classify_all_biomarkers(data)` → threshold results
   - `get_benchmark_data(data)` → percentile points (live or demo source)
   - `find_missing_biomarkers(data)` → flagged blanks
   - `get_medication_notes(data)` → medication caveats
   - `build_physician_guide(threshold_results)` → discussion prompts (non-normal categories only)
   - `get_south_asian_context(bmi)` → only if `south_asian` is true
4. **Assembly** — the router builds a `BenchmarkResponse`. `cohort_label` and `disclaimer` are supplied by model defaults and cannot be absent.
5. **Render** — the frontend stores the response in `sessionStorage`, routes to `/results`, and renders disclaimer → badges → threshold cards → distribution → South Asian context → medication notes → physician guide → limitations. The disclaimer and limitations are unconditional.

---

## 6. The data pipeline (NHANES)

**Source.** NHANES 2017–2018 public XPT files (cycle suffix `_J`), downloaded by `scripts/download_nhanes.py` from the CDC `DataFiles` endpoint. The downloader validates the XPORT magic bytes on each file, because the older CDC URL path now returns HTML "not found" pages with a 200 status that would otherwise be saved as corrupt `.XPT` files.

**Pipeline (live mode).**
1. Read each file, keep `SEQN` + the variables named in `docs/DATA_DICTIONARY.md`, outer-join on `SEQN`.
2. Filter to `RIDRETH3 == 6` (Non-Hispanic Asian).
3. Compute `SBP_mean` / `DBP_mean` as the row-wise mean of the three readings (NaN-aware).
4. Apply the fasting filter: glucose is set to `NaN` for participants who fasted under 8 hours (`PHAFSTHR`), rather than dropping the row — they still contribute their other biomarkers.
5. Rename NHANES variables to internal biomarker keys (`LBDLDL` → `LDL`, etc.).
6. Compute p10/p25/median/p75/p90 and the sample size per biomarker.

**Two real-data corrections** were made during implementation, caught only because the pipeline was built against the actual files rather than assumptions: the 2017–2018 cycle uses the auscultatory BP variables `BPXSY1-3` / `BPXDI1-3` (not the oscillometric `BPXOSY*` names from the 2021+ cycle), and fasting duration `PHAFSTHR` lives in the `FASTQX_J` file, not `GLU_J`. Both are documented in `docs/DATA_DICTIONARY.md`.

**Demo mode** ships the resulting percentiles frozen in `data/demo_cohort.py` so the deployed demo needs no data files and is fully reproducible. The live and demo numbers were verified identical across all nine biomarkers.

---

## 7. The data contract and how it stays in sync

The output shape is defined once in `api/models/results.py` (Pydantic) and mirrored in `frontend/src/lib/types.ts` (TypeScript). The rule, enforced by convention and by the validation gate: **when `results.py` changes, `types.ts` changes in the same commit.** The frontend's types are not independent — they are a transcription of the server contract, and `npm run type-check` will fail if a component reads a field the contract does not define.

`BenchmarkResponse` is the full contract: `threshold_results`, `benchmark_data`, `south_asian_context`, `physician_guide`, `missing_biomarkers`, `medication_notes`, `cohort_label`, `disclaimer`, and `validation_status`.

---

## 8. Testing architecture

The suite has **184 tests across four tiers**, run in order by `scripts/run_validation_gate.sh`:

| Tier | File(s) | Count | What it proves |
|---|---|---|---|
| **Smoke** | `test_smoke.py` | ~32 | Every module imports and every entry point runs on minimal input — catches wiring and signature breaks first |
| **Unit** | `test_thresholds.py`, `test_cohort_filters.py`, `test_missingness.py`, `test_biomarker_mapping.py`, `test_percentile.py` | ~100 | Each function correct in isolation: every threshold boundary, filter behavior, percentile math, real-file sanity checks |
| **Integration** | `test_api_endpoints.py`, `test_integration.py` | ~31 | Components agree through the API: value consistency across sections, guide ⊆ threshold results, context gating |
| **End-to-end** | `test_e2e.py` | ~7 | A real uvicorn server over HTTP: boot, full contract, safety invariants, CORS, input validation |

The unit tier includes boundary cases for every cut-point in the appendix (e.g. LDL at 99/100/129/130/159/160/189/190) and the deliberately tricky HbA1c 6.49 edge. Real-NHANES-file tests skip cleanly when the data is absent, so the suite is green in any environment. A browser-tier checklist for manual or Playwright execution lives in `docs/E2E_CHECKLIST.md`.

**The validation gate** (`scripts/run_validation_gate.sh`) is the single command that must pass before any release: it runs all four test tiers, the TypeScript type-check, a required-docs check, a diagnostic-language scan over the Python source, and structural checks for the cohort filter, HbA1c presence, BP variables, and the fasting filter.

---

## 9. Safety, privacy, and the demo/production boundary

**Statelessness.** No patient biomarker value is written to a database, logged, or persisted server-side. Results exist only in the browser tab's `sessionStorage` and are gone when the tab closes. This is the single most important privacy property and the reason the HIPAA and data-retention surface is minimal.

**Enforced safety invariants** (tested at the unit and e2e tiers):
- `cohort_label` is always exactly `"NHANES Non-Hispanic Asian"` — a Pydantic `Literal`, so any other value is a type error.
- `disclaimer` is a required field (min length 20) and is rendered first on the results page.
- The limitations panel is rendered unconditionally and cannot be collapsed.
- The physician guide is template-generated — there is no LLM call anywhere in `disclaimers.py`.
- No diagnostic or prescriptive language appears in the API source (scanned by the gate) or the served payload (asserted in e2e).
- Medication flags surface a note but never alter a classification.

**The Phase 1 / Phase 2 boundary.** Phase 1 (this system) is a complete, tested, demo-ready educational tool. Production use is gated on Phase 2 work that is intentionally not yet started: licensed-physician review of the clinical output, an FDA Clinical Decision Support (non-device) determination, a published privacy policy, security hardening (rate limiting, dependency remediation), CI/CD, and a WCAG accessibility audit. See `docs/PHASE2_ROADMAP.md`. Until physician review is documented, the tool is for educational demonstration only.

---

## 10. Technology stack and rationale

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 14 (App Router), TypeScript (strict), Tailwind + Material Design 3 | Production-credible UI, type-safe contract, accessible component patterns |
| Backend | FastAPI, Pydantic v2, Uvicorn | Automatic validation and OpenAPI docs; Pydantic enforces the safety invariants |
| Clinical core | Python 3.11+, pandas, numpy, scipy | Standard scientific stack; no web framework dependency keeps it portable and testable |
| Data | NHANES 2017–2018 XPT (live) or frozen percentiles (demo) | Real public reference data with a zero-dependency demo path |
| Tests | pytest, httpx TestClient, real-server e2e | Four-tier coverage from import smoke to live HTTP |

Python is pinned to `>=3.11`; key libraries are version-bounded in `requirements.txt`. The frontend pins Next.js to a patched `14.2.x`. Two `npm audit` high-severity items remain that require a breaking upgrade to Next 16 — deliberately deferred to the Phase 2 security phase rather than destabilize Phase 1.

---

## 11. Deployment model

**Phase 1 (free-tier demo).** Frontend to a static/Next host (e.g. Vercel); backend to a container host (e.g. Render, Railway, or a Hugging Face Space). Because the backend runs in demo mode with no data files, the two can also be collapsed into a single container that serves the built frontend and the API together — one service, no cross-origin wiring. Configuration is via two environment variables: `NEXT_PUBLIC_API_URL` (frontend → backend) and `ALLOWED_ORIGINS` (backend CORS allow-list).

**Phase 2 (production).** Adds CI/CD (test + type-check + build on every PR, deploy on tag), observability, rate limiting, and the clinical/legal/accessibility gates described in `docs/PHASE2_ROADMAP.md`.

---

## 12. Repository map

```
sahc-risklens/
├── CLAUDE.md                  # AI-collaborator operating rules and authority hierarchy
├── README.md                  # Quick start
├── SESSION_START_PROMPT.md    # Per-session task template
├── pyproject.toml             # pytest config (pythonpath, markers), ruff, coverage
├── requirements.txt           # Pinned Python dependencies
│
├── sahc_risklens/             # Clinical core — framework-free Python
│   ├── config.py              #   canonical constants, demo/live detection
│   ├── clinical/              #   biomarkers, thresholds, SA context, disclaimers
│   ├── data/                  #   NHANES loader, filters, missingness, demo cohort
│   └── benchmark/             #   percentile engine
│
├── api/                       # FastAPI tier — thin adapters
│   ├── main.py                #   app + CORS + router registration
│   ├── models/                #   patient.py (input), results.py (authoritative contract)
│   └── routers/               #   benchmark, thresholds, health
│
├── frontend/                  # Next.js 14 + Material Design 3
│   └── src/
│       ├── app/               #   layout, landing, benchmark, results
│       ├── components/        #   form + 6 result components
│       └── lib/               #   types (contract mirror), api client, category styles
│
├── tests/                     # 184 tests across 4 tiers
│   ├── conftest.py            #   9 synthetic patient fixtures
│   ├── test_smoke.py          #   tier 1: imports + entry points
│   ├── test_thresholds.py …   #   tier 2: unit (clinical, data, benchmark)
│   ├── test_*integration*.py  #   tier 3: integration through the API
│   └── test_e2e.py            #   tier 4: real server over HTTP
│
├── docs/                      # Source-of-truth documents
│   ├── PRD.md                 #   product requirements
│   ├── DATA_DICTIONARY.md     #   authoritative NHANES variables
│   ├── CLINICAL_LOGIC_APPENDIX.md  # authoritative thresholds + citations
│   ├── SAFETY_AND_LIMITATIONS.md
│   ├── VALIDATION_PLAN.md
│   ├── RELEASE_CHECKLIST.md
│   ├── PHASE2_ROADMAP.md
│   ├── E2E_CHECKLIST.md
│   └── SESSION_STATUS.md      #   living status + decision log
│
├── scripts/
│   ├── download_nhanes.py     #   fetch + validate XPT files
│   ├── run_validation_gate.sh #   the single pre-release gate
│   └── setup_env.sh           #   venv + npm bootstrap
│
└── .claude/                   # AI reviewer subagents and skills
    ├── agents/                #   clinical_safety, data_qa, release_gate reviewers
    └── skills/                #   implement_feature, run_validation_gate, etc.
```

---

## 13. Extending the system safely

A few rules keep changes from breaking the invariants:

- **Adding or changing a threshold** → edit `docs/CLINICAL_LOGIC_APPENDIX.md` and `sahc_risklens/clinical/thresholds.py` together, add boundary tests, run the gate. Never let the doc and the code diverge.
- **Adding an NHANES variable** → add it to `docs/DATA_DICTIONARY.md` first, then the loader. The Data & QA Auditor subagent checks for divergence.
- **Changing the API response** → update `api/models/results.py` and `frontend/src/lib/types.ts` in the same change; `npm run type-check` enforces the mirror.
- **Any clinical or UI copy change** → re-run the diagnostic-language scan; have the Clinical & Safety Reviewer subagent review before release.
- **Before any release** → `bash scripts/run_validation_gate.sh` must exit clean.

The `.claude/` directory encodes these as reviewer subagents and skills so the discipline survives across development sessions.
