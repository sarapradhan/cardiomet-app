# Contributing to SAHC RiskLens

Thanks for your interest in contributing. SAHC RiskLens is a clinical-safety-first project, so the contribution workflow is built around a single rule: **safety is enforced by code and tests, not by reviewer memory.** Please read this before opening a pull request.

## Ground rules

RiskLens is an educational tool, not a medical device. Any contribution must preserve these boundaries:

- **No diagnosis, no individual risk prediction, no treatment advice** in any patient-facing output.
- **No server-side storage** of patient values — the API stays stateless.
- **No LLM or generated prose** in the patient-facing path — all copy is fixed templates.
- **Honest cohort labeling** — NHANES is a proxy cohort and is never labeled "South Asian."

If a change would weaken any of these, it belongs in a design discussion (open an issue) before any code.

## Where things live (one source of truth per fact)

- Guideline thresholds → `sahc_risklens/clinical/thresholds.py` **only**.
- API response contract → `api/models/results.py`, mirrored to the frontend's `types.ts`.
- Clinical logic → `sahc_risklens/` **only** (this package imports no web framework).
- The API tier (`api/`) validates input and delegates — it contains no clinical logic.
- The frontend renders the API response verbatim and computes nothing clinical.

If you find yourself adding a threshold or a clinical rule outside `sahc_risklens/`, stop — it's in the wrong place.

## Development setup

```bash
bash scripts/setup_env.sh            # backend env + dependencies
python scripts/download_nhanes.py    # optional: public NHANES data
python scripts/build_strata_tables.py# optional: regenerate frozen strata tables
uvicorn api.main:app --reload        # run the API
cd frontend && npm install && npm run dev   # run the frontend
```

## The one command that gates every change

Before opening a PR, run the full validation gate and make sure it is green:

```bash
bash scripts/run_validation_gate.sh
```

This runs all backend test tiers (smoke → unit → integration → e2e), the TypeScript type-check, the **diagnostic-language scan** (fails if patient-facing copy reads as diagnostic or predictive), and the structural checks (cohort filters, fasting filter, BP variable names, trajectory descriptive-only invariant). A PR that does not pass the gate will not be merged.

## Pull request checklist

- [ ] `bash scripts/run_validation_gate.sh` passes clean locally.
- [ ] New clinical logic lives in `sahc_risklens/`, with tests.
- [ ] New thresholds are in `thresholds.py` only, sourced to a named guideline.
- [ ] Any new patient-facing copy is a fixed template and passes the diagnostic-language scan.
- [ ] If you touched the result contract, `results.py` and `types.ts` are both updated.
- [ ] Safety invariants (disclaimer-first, limitations panel, cohort labeling, small-cell suppression) still hold.
- [ ] The PR description explains *why*, and flags any clinical-content change for review.

## Clinical content changes

Changes to thresholds, biomarker categories, or South Asian context notes are **clinical content** and carry extra weight. Cite the guideline and version (e.g. ACC/AHA 2018) in the PR, and expect these to be held for review before merge. When Phase 2 physician review is in place, clinical-content changes will additionally require documented sign-off.

## Reporting issues

Please open an issue for bugs, clinical-accuracy concerns, or safety questions. For anything that could affect patient-facing safety, label it clearly so it can be triaged first.
