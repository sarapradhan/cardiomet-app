cat > CLAUDE.md << 'ENDOFFILE'
# CLAUDE.md — Project context for SAHC RiskLens

This file gives an AI coding assistant the standing context to work in this repo
effectively. Read it first, then the docs referenced below as needed.

## What this project is
SAHC RiskLens is an **educational, non-diagnostic** web app that helps a person
understand their cardiometabolic lab values (lipids, glucose, blood pressure,
body) against published clinical guidelines and a population benchmark, with
**South Asian** risk context that generic tools omit. It also tracks values over
time and generates plain-language questions to bring to a clinician.

It is explicitly **not** a medical device: it does not diagnose, predict
individual risk, or recommend treatment. Those boundaries are load-bearing —
both ethically and as the project's design thesis — and must never be weakened.

## Hard product/safety rules (do not violate)
- **No diagnosis, no prediction, no treatment advice.** Output is descriptive
  ("LDL 168 is in the High category per ACC/AHA") — never "you have X", "your
  10-year risk is Y%", or "start drug Z". There are tests that scan for this;
  keep them passing.
- **The NHANES benchmark cohort is labeled "NHANES Non-Hispanic Asian" — never
  "South Asian".** NHANES has no South Asian–specific cohort. South Asian
  ancestry is surfaced separately as a guideline-recognized *risk-enhancing
  factor*, as qualitative discussion context. Conflating the two is a
  correctness bug and a credibility problem. This distinction is the
  intellectual core of the project.
  - There is now a **second, opt-in cohort** — the *South Asian Heart Center
    clinical cohort* (`config.COHORT_SAHC`, id `sahc`) — a genuine South Asian
    clinical population. It is honestly labeled "South Asian Heart Center
    clinical cohort" and is a *distinct* cohort from NHANES, not a relabeling of
    it. The invariant is: each cohort carries its own honest label, the NHANES
    cohort is never called "South Asian", and the SAHC label is a proper-noun
    cohort name (not the bare phrase "South Asian"). Default cohort is NHANES;
    see `docs/SAHC_COHORT.md`. Tests in `tests/test_sahc_cohort.py` enforce the
    no-crossed-labels invariant.
- **Disclaimers and limitations are always visible and cannot be dismissed.**
- **The server is stateless.** No accounts, no database. Longitudinal data is
  user-owned: exported as a "health file" JSON the user keeps, with an optional
  local-browser cache they control. Don't add server-side persistence.
- **One source of truth for thresholds.** All clinical cut-offs live in
  `sahc_risklens/clinical/thresholds.py`. Never hardcode a threshold elsewhere
  (frontend included) — the frontend renders what the API returns.

## Architecture (three tiers)
- **Clinical core** — `sahc_risklens/`, framework-free Python.
  - `clinical/`: `thresholds.py` (classification + the only thresholds),
    `biomarkers.py` (specs/missing detection), `south_asian_context.py`,
    `disclaimers.py` (template physician guide — no LLM).
  - `data/`: NHANES loader, cohort filters, missingness, demo cohort.
  - `benchmark/percentile.py`: live-vs-demo percentile resolution.
  - `trajectory/`: `series.py` (dated draws, validation), `health_file.py`
    (export/import), `analytics.py` (descriptive-only trend analysis).
- **API** — `api/` (FastAPI, thin). Routers: benchmark, thresholds, health,
  trajectory. Models in `api/models/`. `api/models/results.py` is the
  authoritative response contract; `frontend/src/lib/types.ts` mirrors it.
- **Frontend** — `frontend/` (Next.js 14 + TypeScript, "Quiet Clinical" design).
  Static-exported (`output: 'export'`) and served by FastAPI in one container.
  Key UI: `Legend` (the color language), `ThresholdCards`, `DistributionChart`,
  timeline page + `Timeline`/`TrajectorySummary`, `GuidedTour`, example-patient
  buttons on the benchmark page.

## Data contract sync rule
The Pydantic models in `api/models/` and the TypeScript interfaces in
`frontend/src/lib/types.ts` must stay in lockstep. If you change one, change the
other in the same commit. `npm run type-check` must pass.

## Conventions
- **TDD.** Write/extend tests first, watch them fail, then implement. Tests live
  in `tests/` (backend) and `tests/browser/` (Playwright UI).
- **Design-first for non-trivial work.** There are design docs and build logs in
  `docs/` and `docs/trajectory/`, `docs/cardiosafebench/`. Follow that pattern.
- **Persona reviews** before declaring a feature done: Staff Engineer, Data & QA,
  Clinical & Safety, Frontend/UX. No Blockers allowed.
- Commit style: clear, descriptive messages; conventional prose, not one-liners.

## Build, test, run
# environment
bash scripts/setup_env.sh && source .venv/bin/activate

# full verification (backend + frontend type-check + safety scans + browser UI)
bash scripts/run_validation_gate.sh        # expect: "Validation gate PASSED"

# backend only
python -m pytest tests/ -q --ignore=tests/browser

# browser UI tests (needs: pip install playwright && playwright install chromium,
# and a built static export at frontend/out)
cd frontend && NEXT_PUBLIC_API_URL="" npm run build && cd ..
python -m pytest tests/browser/ -q

# run the whole app as one container (UI + API on one URL)
docker compose up --build                  # http://localhost:8000

# CardioSafeBench safety benchmark
python -m cardiosafebench.run              # writes cardiosafebench/results/

Notes: NHANES .XPT data files are gitignored; the app runs in demo mode without
them (frozen NHANES Non-Hispanic Asian percentiles are baked in). The real-data
tests skip cleanly when the files are absent.

## Deployment
Single container. Dockerfile builds the static frontend (Node) and serves it from
FastAPI (Python). Listens on $PORT (defaults to 7860 for Hugging Face Spaces).
See docs/DEPLOYMENT.md. CI/CD workflows in .github/workflows/.

## CardioSafeBench
cardiosafebench/ is a reproducible safety benchmark: does a guideline-constrained
interpreter avoid the failure modes (diagnosis/prediction/treatment/hallucination/
SA-mislabel) that open-ended interpretation is prone to? It is a constrained-vs-
unconstrained contrast, NOT a multi-vendor leaderboard; the unconstrained arm's
failure rates are a modeled assumption. Keep that limitation explicit anywhere
results are reported — do not overclaim.

## Where to read more
docs/ARCHITECTURE.md (system), docs/PRODUCT_OVERVIEW.md (why/what/personas),
docs/CLINICIAN_BRIEFING.md (the physician-review framing and safety posture),
docs/INCREMENTAL_VALUE_SPEC.md (the differentiation thesis: longitudinal +
verifiable + population-calibrated + user-owned), docs/DATA_DICTIONARY.md
(NHANES specifics and the real-data gotchas), and the build logs under
docs/trajectory/ and docs/cardiosafebench/.
