# SAHC clinical cohort — provenance, governance, and method

This document covers the **South Asian Heart Center (SAHC) clinical cohort**, a
second, separately-labeled benchmark added alongside the NHANES Non-Hispanic
Asian reference. It is the source-of-truth for that cohort's provenance, the
filters and computed columns used, and the caveats that must be surfaced wherever
its numbers appear.

## Why a second cohort

NHANES has no South Asian–specific sample, so the original benchmark uses
**NHANES Non-Hispanic Asian** as a deliberately-labeled *proxy* and surfaces
South Asian ancestry only as a qualitative risk-enhancing factor. The SAHC cohort
is a **genuine South Asian population** (the South Asian Heart Center's
de-identified patients), which lets the app show a real South Asian distribution
*in addition to* — not instead of — the NHANES proxy.

The two cohorts are kept distinct and **honestly labeled**:

| Cohort id (`config.COHORT_*`) | Label (`config.COHORT_LABELS`) | Nature |
|---|---|---|
| `nhanes_asian` | `NHANES Non-Hispanic Asian` | Public population proxy |
| `sahc` | `South Asian Heart Center clinical cohort` | Real South Asian clinic cohort |

**Labeling invariant (enforced by tests):** the NHANES cohort is never labeled
"South Asian"; the SAHC cohort never inherits the NHANES label. This preserves
the proxy-vs-actual distinction that is the project's intellectual core
(CLAUDE.md). The SAHC label is a proper-noun cohort name, not the bare phrase
"South Asian".

## Provenance

- **Source:** El Camino Health — South Asian Heart Center (SCORE program),
  de-identified clinical records (`renamed_merged_data_noPID.csv` in the upstream
  `sahc-tool` repository), imported here as `data/sahc/sahc_cohort_noPID.csv`.
- **Size:** 18,809 rows; the South Asian sub-cohort used here is
  `RIDRETH3 == 1` (n ≈ 9,700 for lipids; smaller for HbA1c/FPG/BP/BMI by
  available measurements).
- **De-identification:** the source carries no patient identifiers ("noPID").

> ⚠️ **Governance gate.** Unlike NHANES (public domain), this is clinic-derived
> data. Before any non-internal deployment, confirm the data-use agreement / IRB
> terms permit aggregate redistribution. As a safeguard the **raw patient CSV is
> never committed** (`.gitignore: data/sahc/*.csv`); only the frozen *aggregate*
> percentiles in `sahc_risklens/data/sahc_demo_cohort.py` are tracked.

## Method (how percentiles are computed)

Mirrors the NHANES pipeline so the two cohorts are comparable:

- Filter to the South Asian sub-cohort (`RIDRETH3 == 1`).
- Map the source's NHANES-style columns to internal biomarker keys
  (`sahc_cohort_loader._BIOMARKER_SOURCE`).
- For each biomarker, drop missing values and compute p10/p25/median/p75/p90 and
  n; biomarkers with fewer than `MIN_COHORT_N` (30) values are omitted.
- **Source resolution:** if `data/sahc/sahc_cohort_noPID.csv` is present,
  percentiles are computed live; otherwise the frozen table in
  `sahc_demo_cohort.py` is used. The frozen numbers are verified to match the
  live computation exactly, so demo and live modes display identical benchmarks.

## Known differences vs the NHANES pipeline (intentional, must stay visible)

These are documented limitations of the SAHC extract, not bugs:

1. **Fasting glucose (FPG):** the extract has no fasting-hours field, so the
   `PHAFSTHR >= 8` fasting filter applied to NHANES FPG cannot be applied here.
   SAHC FPG percentiles therefore include non-fasting draws and should be read as
   "glucose" rather than strictly "fasting glucose".
2. **Blood pressure:** the extract carries a single oscillometric reading per
   patient (`BPXOSY1` / `BPXODI1`); there is no three-reading mean to compute as
   in NHANES.
3. **Clinic vs survey population:** SAHC is an adult cardiometabolic-clinic
   population, so its distributions (notably a much tighter low-BMI tail) differ
   structurally from NHANES's general survey sample.

## Observed cohort differences (illustrative)

The South Asian cohort shows the expected dyslipidemia pattern relative to NHANES
Non-Hispanic Asian — e.g. lower HDL (median 45 vs 52 mg/dL) and higher
triglycerides (median 118 vs 91 mg/dL) — at roughly 10–25× the sample size for
lipids. These are exactly the differences the second cohort exists to surface.

## What did NOT change

- **Classification thresholds** (`clinical/thresholds.py`) are guideline-based
  and cohort-independent — selecting a cohort changes only the *benchmark
  distribution*, never the clinical category.
- The product remains **educational, non-diagnostic**; disclaimers are unchanged
  and always rendered.
- **Default behavior** is unchanged: with no `cohort` parameter the API returns
  the NHANES cohort, so all prior contracts and tests hold.

## Where this is wired

- `sahc_risklens/config.py` — cohort ids, labels, `cohort_label()`.
- `sahc_risklens/data/sahc_cohort_loader.py` — live loader.
- `sahc_risklens/data/sahc_demo_cohort.py` — frozen aggregate percentiles.
- `sahc_risklens/benchmark/percentile.py` — `get_cohort_percentiles(cohort)`,
  `get_benchmark_data(data, cohort)`, `percentile_rank(value, key, cohort)`.
- `api/routers/benchmark.py` — `?cohort=` query parameter (validated).
- `api/models/results.py` — `cohort` + widened `cohort_label` (CohortLabel).
- `frontend/src/lib/types.ts` / `api.ts` — `CohortId`, `COHORT_LABELS`,
  `submitBiomarkers(input, cohort)`.
- `frontend/src/app/benchmark/page.tsx` — the "Compare against" cohort selector.
- `tests/test_sahc_cohort.py` — cohort + label-safety tests.
