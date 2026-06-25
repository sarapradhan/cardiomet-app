---
title: SAHC RiskLens
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
short_description: Educational South Asian cardiometabolic lab context
---

# SAHC RiskLens

**Responsible cardiometabolic benchmarking for South Asian heart health.**
Educational only · Does not diagnose · Discuss results with your clinician.

SAHC RiskLens helps a person understand their own cardiometabolic lab values
(lipids, glucose, HbA1c, blood pressure, body) against published clinical
guidelines and a population benchmark — with **South Asian risk context** that
generic tools omit — and tracks those values over time. It is the safety-
engineered successor to the South Asian Heart Center's original **SCORE** tool.

> It is explicitly **not** a medical device: it does not diagnose, predict
> individual risk, or recommend treatment. Those boundaries are deliberate and
> built into the code and tests.

---

## What it does

For each value a patient enters, RiskLens returns layered, descriptive context:

- **Guideline classification** — the value placed in a named guideline category
  (e.g. "LDL 168 → High, ACC/AHA 2018"). Absolute and population-independent.
- **Population benchmark** — where the value sits in a reference distribution
  (p10–p90), against a **selectable cohort**:
  - *NHANES Non-Hispanic Asian* (a public, reproducible population proxy), or
  - *South Asian Heart Center clinical cohort* (a genuine South Asian population).
- **Peer matching** *(SCORE parity, improved)* — optionally benchmark against the
  patient's matched subgroup (sex + age band + medication use), with small-cell
  suppression and transparent fallback.
- **Advanced lipid markers** — ApoB and Lp(a) classified as guideline risk-
  enhancing factors (classification-only; not cohort-benchmarked).
- **South Asian context** — qualitative, guideline-backed risk-enhancing context
  (ancestry; lower BMI cut-points; elevated Lp(a)), shown when relevant.
- **Longitudinal trajectory** — descriptive trends across dated draws, with data
  owned by the user (exportable health file; nothing stored server-side).
- **Physician discussion guide + pre-visit brief + care navigation** — template
  prompts, a copy-to-clipboard clinician summary, and non-prescriptive next-step
  pointers (family/cascade screening, prevention support).

## What it is not

No diagnosis. No individual risk score or prediction. No treatment advice. No
server-side storage of patient values. Disclaimers and a limitations panel are
always visible and cannot be dismissed.

---

## Architecture (three tiers)

```
Browser ── Next.js 14 + TypeScript (Quiet Clinical UI)
   │  HTTPS  POST /api/v1/benchmark · /trajectory · GET /thresholds · /health
FastAPI (api/) ── thin routers, no clinical logic
   │  in-process calls
sahc_risklens/ ── framework-free Python clinical core
   ├── clinical/    thresholds, biomarkers, SA context, disclaimers, care nav
   ├── data/        NHANES + SAHC loaders, cohort filters, frozen tables
   ├── benchmark/   percentile engine + peer matching
   └── trajectory/  dated series, health file, descriptive analytics
```

The server is **stateless**. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
for the full design.

---

## Quick start

```bash
# Environment (Python venv + frontend deps)
bash scripts/setup_env.sh
source .venv/bin/activate

# (Optional) real NHANES data — the app runs in demo mode without it
python scripts/download_nhanes.py

# (Optional) South Asian Heart Center cohort — place the de-identified CSV at
#   data/sahc/sahc_cohort_noPID.csv   (gitignored; frozen aggregates used otherwise)

# Run (two terminals)
uvicorn api.main:app --reload          # API → http://localhost:8000/docs
cd frontend && npm run dev             # UI  → http://localhost:3000

# Or the whole app as one container
docker compose up --build              # → http://localhost:8000
```

## API at a glance

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/benchmark` | Classify + benchmark a single panel. Query: `?cohort=nhanes_asian\|sahc`, `?match=true` |
| `POST` | `/api/v1/trajectory` | Descriptive trend analysis over a dated series |
| `GET`  | `/api/v1/thresholds` | Full guideline threshold reference |
| `GET`  | `/health` | Liveness + demo/live mode |

Full request/response details: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md).

---

## Testing

```bash
# Backend (294 tests across smoke → unit → integration → e2e)
python -m pytest tests/ -q --ignore=tests/browser

# Frontend contract type-check
cd frontend && npm run type-check

# The single pre-release gate (tests + type-check + safety scans + structural checks)
bash scripts/run_validation_gate.sh    # expect: "Validation gate PASSED"
```

## Key invariants (do not weaken)

- **Descriptive, never diagnostic.** Output describes; it never diagnoses,
  predicts, or prescribes. A diagnostic-language scan runs in the gate.
- **Honest cohort labels.** Each cohort carries its own true label; the NHANES
  cohort is *never* called "South Asian". Enforced by `tests/test_sahc_cohort.py`.
- **One source of truth for thresholds** — `sahc_risklens/clinical/thresholds.py`
  ↔ `docs/CLINICAL_LOGIC_APPENDIX.md`. The frontend renders what the API returns.
- **Contract sync** — `api/models/results.py` ↔ `frontend/src/lib/types.ts` change
  together; `npm run type-check` enforces it.
- **Stateless server** — no accounts, no database; longitudinal data is a
  user-owned health file. Raw patient rows are never committed.

---

## Documentation

Start at the [documentation index](docs/README.md). Highlights:

- [`docs/PRODUCT_DESCRIPTION.md`](docs/PRODUCT_DESCRIPTION.md) — what it is and who it's for
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design
- [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) — endpoints + schemas
- [`docs/FEATURES.md`](docs/FEATURES.md) — feature-by-feature guide
- [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) — setup, conventions, extending
- [`docs/SAHC_COHORT.md`](docs/SAHC_COHORT.md) — cohort provenance, peer matching, governance
- [`docs/CLINICAL_LOGIC_APPENDIX.md`](docs/CLINICAL_LOGIC_APPENDIX.md) — thresholds + citations
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) — NHANES variables
- [`docs/CLINICIAN_BRIEFING.md`](docs/CLINICIAN_BRIEFING.md) — the physician-review framing
- [`docs/SAFETY_AND_LIMITATIONS.md`](docs/SAFETY_AND_LIMITATIONS.md) · [`docs/PHASE2_ROADMAP.md`](docs/PHASE2_ROADMAP.md)

## Status

Phase 1 — educational demonstration. Production use is gated on documented
clinician review of the clinical output, a regulatory (non-device CDS)
determination, and the security/accessibility work in
[`docs/PHASE2_ROADMAP.md`](docs/PHASE2_ROADMAP.md). The ApoB/Lp(a) thresholds and
the SAHC cohort are marked for clinician sign-off.
