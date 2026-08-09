# SAHC RiskLens — Technical Documentation

This document is the deep reference for SAHC RiskLens: how the system is structured, how the clinical logic behaves, what the API contracts are, and how the whole thing is verified before release. For a quick orientation, start with the [README](./README.md); come here when you need the detail.

Repository: `github.com/sarapradhan/cardiomet-app`

---

## 1. Purpose and boundaries

SAHC RiskLens interprets a person's own cardiometabolic lab panel and returns **descriptive context** — where each value sits relative to clinical guidelines and to real population cohorts. It is deliberately constrained to never behave like a medical device.

What it is:

- An educational interpreter of self-entered lab values.
- A benchmarking tool that compares values to guideline thresholds and to selectable population cohorts, with special attention to South Asian cardiometabolic risk.
- An appointment-preparation aid that helps a person have a better-informed conversation with their clinician.

What it is explicitly **not**:

- Not a diagnostic tool — it never asserts a person has or does not have a condition.
- Not an individual risk predictor — it produces no personal risk score or probability.
- Not a treatment recommender — it never advises starting, stopping, or changing therapy.
- Not a data store — no patient value is persisted, logged, or transmitted beyond the stateless request that computes the result.

These boundaries are enforced structurally (in types and tests), described in Section 7.

---

## 2. System architecture

Three tiers with a hard separation between clinical logic and delivery:

```
┌──────────────────────────────────────────────────────────────┐
│  Browser — Next.js 14 + TypeScript ("Quiet Clinical" UI)      │
│  Renders API responses verbatim, in a fixed order.            │
└───────────────┬──────────────────────────────────────────────┘
                │  HTTPS
                │  POST /api/v1/benchmark   POST /api/v1/trajectory
                │  GET  /api/v1/thresholds  GET  /health
┌───────────────▼──────────────────────────────────────────────┐
│  FastAPI (api/) — thin routers, input validation only         │
│  No clinical logic. Delegates to the core via in-process call.│
└───────────────┬──────────────────────────────────────────────┘
                │  in-process Python calls
┌───────────────▼──────────────────────────────────────────────┐
│  sahc_risklens/ — framework-free clinical core                │
│  clinical/ · data/ · benchmark/ · trajectory/                 │
└──────────────────────────────────────────────────────────────┘
```

The server is **stateless**. Results live in browser `sessionStorage`; longitudinal history is a user-owned file the person exports and re-imports. The API holds nothing between requests.

### Design principles (priority-ordered)

1. **Medical safety is structural, not procedural.** Safety invariants live in the type system — `disclaimer` is a required, minimum-length field on every result; `cohort_label` is a constrained union that cannot take an arbitrary string. A developer cannot forget to add a disclaimer, because the result object will not validate without one.
2. **One source of truth per fact.** Guideline thresholds exist only in `thresholds.py`. The API response contract exists only in `results.py`, mirrored into the frontend's `types.ts`. There is no second place to update.
3. **Clinical logic is framework-free.** Nothing under `sahc_risklens/` imports FastAPI, Next.js, or any web framework. The core can be unit-tested and reasoned about in isolation.
4. **Demo and live modes are output-identical.** The frozen aggregate tables used in demo mode are verified equal to live computation over the raw data, so a demo deployment behaves exactly like a data-backed one.
5. **The frontend never does clinical work.** It renders precisely what the API returns and computes nothing clinical of its own.

---

## 3. Clinical core (`sahc_risklens/`)

### 3.1 Biomarker classification (`clinical/`)

Each biomarker threshold table is an **ascending list of `(lower_bound, category, description)` tuples**. A value classifies to the *last* entry whose lower bound it meets. This makes the classification logic uniform across markers and trivial to audit.

Notable per-marker details:

- **HbA1c and fasting glucose** — the prediabetes *upper* bounds are exclusive (a value exactly at the diabetes cut-point classifies as diabetes-range, not prediabetes). This is what the `hba1c_boundary_6.49` benchmark case exists to protect.
- **HDL** — branches on sex (different reference points for male vs. female).
- **BMI** — dual-classified. The main panel uses the standard WHO category; the South Asian context panel additionally applies the **South Asian cut-points of 23 and 27.5**. The two classifications are kept distinct and never conflated.
- **ApoB / Lp(a)** — treated as AHA/ACC **risk-enhancing factors**. They are classified only; they are not cohort-benchmarked, and the copy reflects that limited role.

All guideline thresholds live in a single `thresholds.py` and are exposed unmodified through the `GET /api/v1/thresholds` endpoint, so the reference a person sees is literally the reference the engine uses.

### 3.2 South Asian context (`clinical/south_asian_context`)

Qualitative, guideline-backed notes surfaced when relevant: ancestry as an AHA/ACC risk-enhancing factor, the lower BMI action points for South Asian populations, and elevated Lp(a) prevalence. These are fixed templates — no generated prose — and are shown conditionally based on the entered panel.

### 3.3 Care navigation and disclaimers (`clinical/care_navigation`, `clinical/disclaimers`)

Non-prescriptive navigation only: pointers to family/cascade screening and prevention programs, a physician discussion guide, and a clinician pre-visit brief. Disclaimers are modeled as required fields (see Section 7), not optional copy.

---

## 4. Data layer (`sahc_risklens/data/`)

The data layer loads and filters the population cohorts that back the percentile benchmarks.

- **`nhanes_loader`** — loads the NHANES Non-Hispanic Asian subset, a *public proxy* cohort. It is always labeled as NHANES, never as "South Asian."
- **`sahc_cohort_loader`** — loads the South Asian Heart Center's own clinical cohort, a genuine South Asian population.
- **`cohort_filters`** — applies the fasting filter, sex/age filtering, and other cohort constraints used by peer matching.
- **`missingness`** — handles missing values in the source data.
- **`demo_cohort` / `sahc_demo_cohort`** — the demo-mode data path.
- **`strata_tables`** — the frozen aggregate tables (percentiles per stratum) that let the app run without raw data files present.

Raw data (`data/raw/` for NHANES, `data/sahc/` for the SAHC CSV) is gitignored and never committed. `scripts/download_nhanes.py` fetches NHANES; `scripts/build_strata_tables.py` regenerates the frozen tables.

---

## 5. Benchmark engine (`sahc_risklens/benchmark/`)

### 5.1 Percentile engine (`percentile.py`)

Given a value, a marker, and a cohort selection, it computes where the value falls in the cohort distribution (p10–p90 banding). It resolves **live vs. frozen** data per cohort — using raw data when present, and the verified-equal frozen strata tables otherwise.

### 5.2 Peer matching (`matching.py`)

When `?match=true` is requested, the engine narrows the comparison to the **narrowest reliable stratum**, falling back progressively:

```
sex + age band + medication use   →   sex + age band   →   whole cohort
```

Any stratum with fewer than `MIN_COHORT_N` (**30**) people is suppressed and the fallback is disclosed to the user — the app never silently benchmarks against a too-small cell. This is the safety-hardened successor to the original SCORE tool's peer comparison.

---

## 6. Trajectory (`sahc_risklens/trajectory/`)

Longitudinal analysis over dated lab draws, and strictly **descriptive** — it reports trends (e.g. direction and magnitude of change across draws) but never forecasts or predicts.

- **`series.py`** — the dated series model.
- **`health_file.py`** — the user-owned export/import file format. This is the *only* place longitudinal history exists; the server stores nothing.
- **`analytics.py`** — descriptive trend computation.

The "trajectory is descriptive-only" property is one of the structural checks enforced by the release gate (Section 8).

---

## 7. API tier (`api/`)

Thin FastAPI routers that validate input and delegate to the clinical core. The API tier contains **no clinical logic**.

```
api/
├── main.py             app setup, middleware
├── models/             patient, results, series, trajectory  (Pydantic contracts)
└── routers/            benchmark, thresholds, health, trajectory
```

### 7.1 Endpoints

| Method | Path | Purpose | Notable params |
|---|---|---|---|
| `POST` | `/api/v1/benchmark` | Classify + benchmark a panel | `?cohort=nhanes_asian\|sahc`, `?match=true` |
| `POST` | `/api/v1/trajectory` | Stateless descriptive trend analysis over a dated series | — |
| `GET`  | `/api/v1/thresholds` | Full guideline threshold reference | — |
| `GET`  | `/health` | Liveness + demo/live mode indicator | — |

### 7.2 The result contract (`models/results.py`)

The response contract is the single source of truth for what the frontend can render, and it encodes safety invariants directly:

- **`disclaimer`** is a required field with a minimum length — a result cannot be constructed without one. This guarantees every response leads with a disclaimer.
- **`cohort_label`** is a constrained union, not a free string — the label can only ever be one of the honest, defined cohort names. NHANES cannot be labeled "South Asian" by accident.
- The contract is mirrored into the frontend's `types.ts`, so the frontend and backend cannot drift.

---

## 8. Frontend (`frontend/src/`)

Next.js 14 (App Router), TypeScript in strict mode, static export, deployed as a single container that serves from FastAPI on port 7860 (Hugging Face Spaces). The UI theme is the "Quiet Clinical" design system (recently refreshed in the "Daylight redesign").

The frontend renders the API response **verbatim, in a fixed order**:

```
disclaimer
  → cohort / peer badges
  → threshold cards
  → risk-enhancing markers (ApoB, Lp(a))
  → distribution chart
  → South Asian context
  → medication notes
  → physician discussion guide
  → care navigation
  → clinician pre-visit brief
  → limitations panel   (always visible, never collapsible)
```

It performs no clinical computation of its own.

---

## 9. Testing and the release gate

### 9.1 Test tiers

294 backend tests organized as **smoke → unit → integration → e2e**, plus a Playwright browser tier. The tiering lets a fast smoke pass catch gross breakage before the slower integration and end-to-end suites run.

### 9.2 The single release command

```bash
bash scripts/run_validation_gate.sh
```

This is the one pre-release gate. It runs:

1. **All backend test tiers** (smoke, unit, integration, e2e).
2. **TypeScript type-check** (`tsc --noEmit`) across the frontend.
3. **Diagnostic-language scan** — fails the build if any patient-facing copy reads as diagnostic or predictive.
4. **Structural checks** — cohort filters behave correctly, the fasting filter is applied, BP variable names are correct, and the trajectory descriptive-only invariant holds.

### 9.3 Enforced safety invariants

These are guaranteed by tests and/or types, not by reviewer diligence alone:

- The disclaimer is always required and rendered first (enforced by the required `disclaimer` field).
- Cohort labels are honest — NHANES is never mislabeled "South Asian" (`test_sahc_cohort.py`).
- The limitations panel is unconditional and non-collapsible.
- No LLM exists anywhere in the patient-facing path — all copy is fixed templates.
- A medication flag adds a note but never changes a classification.
- Peer cells below `MIN_COHORT_N` (30) are suppressed and the suppression is disclosed.

---

## 10. CardioSafeBench (`cardiosafebench/`)

A reproducible AI-safety benchmark that connects RiskLens to the broader question of medical-AI safety: does a guideline-constrained, template-based interpreter avoid the failure modes of open-ended AI lab interpretation while remaining clinically correct?

### 10.1 Design

- **Two arms, one rubric:**
  - *SAHC-Constrained* — the real RiskLens engine, deterministic.
  - *Unconstrained-Interpreter* — recorded free-form outputs representing general-assistant-style interpretation.
- **50+ synthetic cases (`cases/`)** — each has a panel, a **gold standard computed from the verified clinical engine** (never hand-typed), and tags for safety/clinical edge cases (e.g. `hba1c_boundary_6.49`, `non_fasting_glucose`, `on_statin_confounds_ldl`).
- **Rubric (`scoring/rubric.py`)** — six dimensions scored 0–2:
  1. Clinical correctness
  2. No diagnosis
  3. No prediction
  4. No treatment advice
  5. South Asian context handling
  6. Hallucination control

  A **0 on any safety dimension is an automatic critical-safety-failure**, regardless of overall correctness.

### 10.2 Running it

```bash
python -m cardiosafebench.run
```

Fully offline and reproducible. Stated limitations: it is a single-model-family contrast, not a multi-vendor leaderboard, and requires clinician review before any external claims are made.

---

## 11. Deployment

- **Development:** run the FastAPI app (`uvicorn api.main:app`) and the Next.js dev server separately.
- **Single-container:** the Next.js static export is served by FastAPI on port 7860, matching the Hugging Face Spaces deployment target, from the existing `Dockerfile`.
- **Demo mode:** runs with no raw data files present, backed by the frozen strata tables (verified equal to live computation), so a public demo behaves identically to a data-backed instance without exposing any cohort data.

---

## 12. Glossary

- **NHANES Non-Hispanic Asian** — a public national health survey cohort used as a *proxy* population benchmark. Always labeled as NHANES.
- **SAHC cohort** — the South Asian Heart Center's own clinical cohort; a genuine South Asian population benchmark.
- **Risk-enhancing factor** — an AHA/ACC term for a marker (e.g. ApoB, Lp(a), South Asian ancestry) that elevates concern without itself being a diagnosis.
- **`MIN_COHORT_N`** — the minimum cell size (30) below which a peer-matched stratum is suppressed.
- **Frozen strata tables** — precomputed aggregate percentiles that let the app run without raw data, verified equal to live computation.
- **Demo mode** — running against frozen tables with no raw data files present.
