# CardioMet Lens — Developer Guide

How to set up, run, test, and safely extend the app. Read
[`ARCHITECTURE.md`](ARCHITECTURE.md) first for the big picture.

---

## Prerequisites

- Python ≥ 3.11
- Node.js 18+ (for the Next.js frontend)
- (Optional) Docker, for single-container runs

## Setup

```bash
bash scripts/setup_env.sh        # creates .venv and installs Python + frontend deps
source .venv/bin/activate
```

Data is optional — the app runs in **demo mode** using frozen aggregate tables:

- **NHANES:** `python scripts/download_nhanes.py` fetches + validates the XPT
  files into `data/raw/` (gitignored). Without them, the frozen NH-Asian
  percentiles in `data/demo_cohort.py` are used.
- **SAHC cohort:** place the de-identified CSV at `data/sahc/sahc_cohort_noPID.csv`
  (gitignored). Without it, `data/sahc_demo_cohort.py` + `data/strata_tables.json`
  are used. Regenerate the frozen tables with
  `python scripts/build_strata_tables.py` when the CSV changes.

## Run

```bash
# Two-terminal dev
uvicorn api.main:app --reload          # API → http://localhost:8000/docs
cd frontend && npm run dev             # UI  → http://localhost:3000

# Single container (builds static frontend, serves it from FastAPI)
docker compose up --build              # → http://localhost:8000
```

Environment variables: `NEXT_PUBLIC_API_URL` (frontend → backend, empty string
when co-hosted), `ALLOWED_ORIGINS` (backend CORS), `SAHC_MODE`, `NHANES_DATA_DIR`,
`SAHC_DATA_DIR`/`SAHC_DATA_FILE`.

## Test

```bash
# Backend (excludes the browser tier)
python -m pytest tests/ -q --ignore=tests/browser

# A single suite
python -m pytest tests/test_peer_matching.py -q

# Frontend contract type-check
cd frontend && npm run type-check

# Browser tier (needs a built export + Playwright)
cd frontend && NEXT_PUBLIC_API_URL="" npm run build && cd ..
python -m pytest tests/browser/ -q

# The single pre-release gate (run this before any PR)
bash scripts/run_validation_gate.sh    # expect: "Validation gate PASSED"
```

The gate runs all backend tiers + TypeScript type-check + a required-docs check +
a diagnostic-language scan + structural checks (cohort filter, HbA1c, BP vars,
fasting filter, trajectory descriptive-only).

---

## Conventions

- **TDD.** Write/extend tests first, watch them fail, then implement. Backend tests
  in `tests/`, browser tests in `tests/browser/`.
- **Design-first** for non-trivial work; follow the patterns in `docs/`.
- **Commit style:** clear, descriptive prose messages.
- **No clinical logic in the frontend or routers.** The browser renders what the
  API returns; routers validate and delegate to `sahc_risklens/`.

## The load-bearing rules

1. **Thresholds:** one source of truth — `clinical/thresholds.py` ↔
   `CLINICAL_LOGIC_APPENDIX.md`. Change both together; add boundary tests.
2. **NHANES variables:** only in `DATA_DICTIONARY.md` + the loader.
3. **API contract:** `api/models/results.py` ↔ `frontend/src/lib/types.ts` in the
   same commit. `npm run type-check` enforces it.
4. **Cohort labels:** each cohort keeps its own honest label; the NHANES cohort is
   never "South Asian". `tests/test_sahc_cohort.py` enforces it.
5. **Descriptive only:** no diagnosis/prediction/treatment language anywhere in
   the served payload or source (scanned by the gate).
6. **Stateless:** no server-side persistence; never commit raw patient rows.

---

## Common tasks

### Add or change a threshold
Edit `CLINICAL_LOGIC_APPENDIX.md` and `clinical/thresholds.py` together → add
boundary tests in `tests/test_thresholds.py` → run the gate.

### Add a benchmark cohort
1. Loader in `data/` (biomarker frame + matching frame), filtered to the cohort.
2. Frozen aggregate table (`*_demo_cohort.py`) verified equal to live.
3. A `COHORT_*` id + label in `config.py` and `COHORT_LABELS`.
4. Register it in `benchmark/percentile.py` (`SUPPORTED_COHORTS`, source
   resolution) and, for matching, generate a strata table.
5. Extend `tests/test_sahc_cohort.py` (incl. the no-crossed-labels invariant) and
   document provenance in `SAHC_COHORT.md`.

### Add a peer-matching dimension
Extend `benchmark/matching.py` (strata key, level predicates, description),
regenerate `strata_tables.json` via `scripts/build_strata_tables.py` (keep the
small-cell suppression), and add tests in `tests/test_peer_matching.py`.

### Add a classification-only marker (like ApoB/Lp(a))
Add a table + entry in `_RISK_ENHANCERS` (`thresholds.py`), an input field in
`api/models/patient.py` and `types.ts`, a form field, render it via
`RiskEnhancingMarkers.tsx`, and add tests. Do **not** add it to the benchmarked
core set unless a cohort measures it.

### Change the API response
Update `results.py` and `types.ts` together; update any component that reads the
new field; run `npm run type-check` and the gate.

---

## Repository orientation

- `sahc_risklens/` — clinical core (clinical/, data/, benchmark/, trajectory/).
- `api/` — FastAPI routers + Pydantic models.
- `frontend/src/` — `app/` pages, `components/`, `lib/`.
- `tests/` — smoke → unit → integration → e2e (+ `tests/browser/`).
- `scripts/` — env setup, NHANES download, strata-table build, validation gate.
- `docs/` — this guide and the source-of-truth documents.
- `cardiosafebench/` — reproducible safety benchmark.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) §12 for the full map.
