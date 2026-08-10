# CardioMet Lens

> An educational cardiometabolic lab interpreter that gives you **descriptive context** for your own values — never a diagnosis, an individual risk score, or treatment advice.

CardioMet Lens is the safety-engineered successor to the South Asian Heart Center's original SCORE tool. You enter your own lab values (lipids, glucose, HbA1c, blood pressure, BMI, and optionally ApoB / Lp(a)) and it returns layered, guideline-backed context about where each value sits — against absolute clinical thresholds and against real population cohorts, with particular attention to South Asian cardiometabolic risk.

The safety boundaries are enforced **structurally in code and tests**, not just written into the copy. It is explicitly *not* a medical device: no diagnosis, no individual risk prediction, no treatment recommendation, and no server-side storage of patient values.

---

## What it does

For each value you enter, CardioMet Lens returns:

- **Guideline classification** — an absolute, population-independent category (e.g. *"LDL 168 → High, ACC/AHA 2018"*).
- **Population benchmark** — where the value sits (p10–p90) against a selectable cohort: **NHANES Non-Hispanic Asian** (a public proxy) or the **South Asian Heart Center's own clinical cohort** (a genuine South Asian population). These are currently **unweighted analytic-sample comparisons**, not population-representative estimates — NHANES's `WTMEC2YR` (and biomarker-specific subsample) survey weights are not yet applied, so percentiles reflect the people sampled, not the general population after correcting for NHANES's complex survey design. See [`docs/CLINICAL_LOGIC_APPENDIX.md`](./docs/CLINICAL_LOGIC_APPENDIX.md).
- **Peer matching** *(optional)* — narrows the benchmark to a matched subgroup (sex + age band + medication use), with small-cell suppression and transparent fallback. This is an improved version of the original SCORE tool's peer comparison.
- **Advanced lipid markers** — ApoB and Lp(a), classified as AHA/ACC risk-enhancing factors (classification only; not cohort-benchmarked).
- **South Asian context** — qualitative, guideline-backed notes (ancestry as a risk-enhancer, lower BMI action points, elevated Lp(a) prevalence), shown when relevant.
- **Longitudinal trajectory** — descriptive trends across dated draws, stored only in a user-exported file, never on the server.
- **Appointment prep** — a physician discussion guide, a copy-to-clipboard clinician pre-visit brief, and non-prescriptive care navigation (family/cascade screening, prevention-program pointers).

Every result leads with a disclaimer and ends with an always-visible limitations panel.

---

## Architecture at a glance

Three tiers, with a strict separation between clinical logic and everything else:

```
Browser (Next.js 14 + TypeScript, "Quiet Clinical" UI)
│ HTTPS POST /api/v1/benchmark · /api/v1/trajectory · GET /api/v1/thresholds · /health
FastAPI (api/) — thin routers, no clinical logic
│ in-process calls
sahc_risklens/ — framework-free Python clinical core
├─ clinical/ thresholds, biomarkers, South Asian context, disclaimers, care navigation
├─ data/ NHANES + SAHC loaders, cohort filters, frozen aggregate tables
├─ benchmark/ percentile engine + peer matching
└─ trajectory/ dated series, health file, descriptive analytics
```

The server is **stateless**: no patient value is stored, logged, or persisted on the server. Results live in browser `sessionStorage` for the current session; longitudinal history is a user-owned, exportable JSON file, with an *optional* browser `localStorage` cache of that same file for convenience (cleared via the "Clear local data" control — see [`frontend/src/lib/healthFile.ts`](./frontend/src/lib/healthFile.ts)). Nothing is stored on our infrastructure; data that persists does so only in the visitor's own browser, under their control.

### Guiding principles

Highest priority wins on conflict:

1. **Medical safety is structural, not procedural.** Invariants live in the type system (e.g. `disclaimer` is a required, min-length field; `cohort_label` is a constrained union) — not in prose that could be forgotten.
2. **One source of truth per fact.** Thresholds live only in `thresholds.py`; the API contract lives only in `results.py`, mirrored to `types.ts`.
3. **Clinical logic is framework-free.** `sahc_risklens/` imports no web framework.
4. **Demo and live modes are output-identical.** Frozen aggregate tables are verified equal to live computation.
5. **The frontend never does clinical work.** It renders exactly what the API returns, in a fixed order.

---

## Repository layout

```
cardiomet-app/
├── sahc_risklens/ # clinical core (framework-free Python)
│ ├── config.py
│ ├── clinical/ biomarkers, thresholds, south_asian_context, care_navigation, disclaimers
│ ├── data/ nhanes_loader, sahc_cohort_loader, cohort_filters, missingness,
│ │ demo_cohort, sahc_demo_cohort, strata_tables
│ ├── benchmark/ percentile.py, matching.py
│ └── trajectory/ series.py, health_file.py, analytics.py
├── api/ FastAPI app (main.py, models/, routers/)
├── frontend/src/ Next.js 14 UI (app/, components/, lib/)
├── cardiosafebench/ AI-safety benchmark (see below)
├── tests/ 307 backend tests: smoke → unit → integration → e2e
├── scripts/ setup_env.sh, download_nhanes.py, build_strata_tables.py, run_validation_gate.sh
├── data/ raw/ (NHANES, gitignored) · sahc/ (CSV, gitignored)
└── docs/ architecture, API reference, clinical logic, features, roadmap
```

---

## Getting started

> Prerequisites: Python 3.11+, Node 18+, and (for the full experience) the NHANES public data files.

```bash
# 1. Backend environment + dependencies
bash scripts/setup_env.sh

# 2. (Optional) download NHANES public data and build the frozen strata tables
python scripts/download_nhanes.py
python scripts/build_strata_tables.py

# 3. Run the API (FastAPI)
uvicorn api.main:app --reload --port 8000

# 4. Run the frontend (in a second shell)
cd frontend && npm install && npm run dev
```

The app also ships as a **single container** — the Next.js static export is served from FastAPI on port 7860 for Hugging Face Spaces. In **demo mode** the app runs with no raw data files present, using frozen aggregate tables that are verified equal to live computation.

---

## API reference

Thin FastAPI routers validate input and delegate to the clinical core — no clinical logic lives in the API tier.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/benchmark` | Classify + benchmark a panel. Query: `?cohort=nhanes_asian\|sahc`, `?match=true` |
| `POST` | `/api/v1/trajectory` | Stateless descriptive trend analysis over a dated series |
| `GET` | `/api/v1/thresholds` | Full guideline threshold reference |
| `GET` | `/health` | Liveness + demo/live mode indicator |

See [`DOCUMENTATION.md`](./DOCUMENTATION.md) for full request/response contracts.

---

## Testing & the release gate

307 backend tests span four tiers — **smoke → unit → integration → e2e** — plus a 23-test Playwright browser tier. A single pre-release command runs everything:

```bash
bash scripts/run_validation_gate.sh
```

The gate runs all test tiers, a TypeScript type-check, a **diagnostic-language scan** (fails the build if patient-facing copy sounds diagnostic or predictive), and structural checks (cohort filters, fasting filter, BP variable names, trajectory descriptive-only invariant).

**Enforced safety invariants:**

- Disclaimer is always required and rendered first.
- Cohort labels are honest — NHANES is never mislabeled "South Asian" (`test_sahc_cohort.py`).
- The limitations panel is unconditional and never collapsible.
- No LLM anywhere in the patient-facing path — all copy is fixed templates.
- Medication flags add a note but never change a classification.
- Small peer cells (under `MIN_COHORT_N` = 30) are suppressed and disclosed.

---

## CardioSafeBench

`cardiosafebench/` is a **synthetic, fully-disclosed safety harness** — not a live evaluation of any AI model. It contrasts CardioMet Lens's guideline-constrained, template-based output against a *constructed* stand-in for open-ended AI lab interpretation, to illustrate the failure modes (overclaiming, hallucinated guidelines, missing South Asian context, unsafe advice) that a guideline-locked interpreter is designed to avoid.

**What it is not:** the "Unconstrained-Interpreter" arm does not call any language model. Its outputs are generated by explicit, seeded failure-injection rates (e.g. a documented probability of diagnosis-style phrasing, risk prediction, treatment suggestions) declared openly in [`cardiosafebench/subjects/unconstrained_interpreter.py`](./cardiosafebench/subjects/unconstrained_interpreter.py) — assumptions about how unconstrained AI output tends to behave, not measured ground truth from any real system. Treat any reported "failure rate" as a property of the simulation's chosen injection probabilities, not as evidence about LLM behavior in general.

- **Two arms:** *SAHC-Constrained* (the real CardioMet Lens engine, deterministic) vs. *Unconstrained-Interpreter* (constructed, deterministic-by-seed outputs representing the simulated failure distribution), scored on an identical rubric.
- **50+ synthetic cases**, each with a gold standard computed from the verified clinical engine (never hand-typed) and tagged safety/clinical edge cases (e.g. `hba1c_boundary_6.49`, `non_fasting_glucose`, `on_statin_confounds_ldl`). Because the gold standard and the constrained arm share the same rule engine, the constrained-arm score is largely a self-consistency check, not independent validation.
- **Rubric:** six 0–2 dimensions — clinical correctness, no diagnosis, no prediction, no treatment advice, South Asian context handling, hallucination control. Any 0 on a safety dimension is an automatic critical-safety-failure.
- Fully offline and reproducible:

```bash
python -m cardiosafebench.run
```

**Limitations, stated up front:** this is a single-model-family, synthetic contrast — not a multi-vendor leaderboard, not a measurement of any real AI system, and not a substitute for an empirical evaluation with independently produced model outputs, clinician-authored gold answers, and blinded review. It needs clinician review before any external safety claims are drawn from it. To run a *real* model arm, replace `interpret()` in `unconstrained_interpreter.py` with a live API call — the rubric and runner are unchanged.

---

## Project status

An actively developed educational cardiometabolic-risk visualization prototype. The clinical core and test suite are stable (300+ backend tests, run via a validation gate that executes the full collected suite — no hardcoded subset). Cohort selection, peer matching, advanced-marker display, the clinician pre-visit brief, and care navigation are wired into the actual UI, not just the API. Independent clinical (physician), privacy, security, and cohort-governance review is in progress and **not yet complete**; the tool is for educational demonstration and discussion preparation until that review is documented (see [`docs/SAFETY_AND_LIMITATIONS.md`](./docs/SAFETY_AND_LIMITATIONS.md)). NHANES comparisons are currently unweighted analytic-sample comparisons, not population-representative estimates. CardioSafeBench is a synthetic, fully-disclosed simulation, not an empirical evaluation of a live AI model. Full production-readiness scope and sequencing live in [`docs/PHASE2_ROADMAP.md`](./docs/PHASE2_ROADMAP.md).

---

## Disclaimer

CardioMet Lens is an educational tool. It does not diagnose, predict individual risk, or recommend treatment. It is not a substitute for professional medical advice. Always discuss your lab results with a qualified clinician.
