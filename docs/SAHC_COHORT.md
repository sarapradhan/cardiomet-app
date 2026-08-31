# The removed "sahc" cohort — provenance record

**Status: removed on 2026-08-30. This document is the record of why.**

CardioMet Lens shipped a second benchmark cohort, id `sahc`, alongside the NHANES
Non-Hispanic Asian reference. It was removed because its provenance could not be
established. This document replaces the previous one, which described the cohort
as current and attributed it to a named clinical program.

---

## 1. What was removed

| Artifact | Was |
|---|---|
| `sahc_risklens/data/sahc_demo_cohort.py` | Frozen whole-cohort percentiles for 9 biomarkers |
| `sahc_risklens/data/strata_tables.json` | 23 strata × 197 biomarker cells of stratified percentiles |
| `sahc_risklens/data/sahc_cohort_loader.py` | Loader for the source CSV |
| `scripts/build_strata_tables.py` | Generator for the stratified table |
| `COHORT_SAHC`, `SAHC_COHORT_LABEL`, `SAHC_DATA_FILE` | Cohort registration in `config.py` |
| Cohort selector, "Match to peers" toggle | Frontend controls that depended on it |

`?cohort=sahc` now returns **422**, the same as any other unknown cohort id.

## 2. Why

The frozen aggregates were computed in June 2026 from a CSV at
`data/sahc/sahc_cohort_noPID.csv`. That file no longer exists and was not
recovered, so its contents cannot be inspected.

The previous version of this document attributed it to El Camino Health's South
Asian Heart Center (SCORE program) and cited `renamed_merged_data_noPID.csv` in
the upstream `sahc-tool` repository as the source. **That citation is false.** The
upstream repository was checked across its complete history: no such file exists
there or in any commit. It contains only public NHANES data, with an incompatible
schema and a different row count (15,560 vs the 18,809 claimed here).

With the source gone and the one written provenance claim demonstrably wrong,
there was no basis on which to keep publishing the numbers or the attribution.

## 3. What the artifacts did establish, before removal

Recorded here because it is the only surviving evidence about the source, and a
future decision may need it.

The two frozen tables were generated on different days by different code paths
(`sahc_demo_cohort.py` 2026-06-22; `strata_tables.json` 2026-06-23) and reconciled
with each other to a structured, per-panel missingness pattern — the sum of each
biomarker's counts across the eight mutually exclusive sex × age strata fell short
of the whole-cohort count by a fixed amount per clinical panel (−52 for all four
lipids, −299 for both blood-pressure measures, −27 HbA1c, −24 glucose, −289 BMI).
That pattern is produced by computing quantiles over a real tabular dataset with
differential missingness, not by generating plausible numbers.

From that reconciliation alone:

- ~18,255 records carried a usable sex and age; ~9,750 a full lipid panel; ~8,800
  blood pressure and BMI; 6,046 HbA1c; 4,497 glucose.
- The source carried columns named `RIDRETH3, RIAGENDR, RIDAGEYR, LBDLDL, LBDHDD,
  LBXTR, LBXTC, LBXGH, LBXGLU, BPXOSY1, BPXODI1, BMXBMI` (NHANES variable naming)
  plus `cholMeds`, `bpMeds`, `diabMeds` (not NHANES).
- The `RIDRETH3 == 1` filter selected essentially the whole file, so the ethnicity
  field was near-constant.
- The distribution was lean with low HDL and high triglycerides (median BMI 25.2,
  HDL 45, TG 118) — a South Asian cardiometabolic phenotype, not a US
  general-population profile.

**What was never established:** the institution, study, or system the records came
from; whether they were clinical, research, or survey records; whether any
permission covered their use; and the exact row count.

## 4. What was never at risk

No patient rows were ever committed. `.gitignore` excluded `data/sahc/*.csv`, and
every commit on every branch was checked for any `.csv`, `.xlsx`, or `noPID` file
— there are none. Only aggregates were tracked, with a minimum cell size of 30
enforced at generation time. The exposure here was a claim about provenance, not
a disclosure of data.

## 5. The seam that was deliberately kept

The cohort is gone; the architecture that hosted it is not. Still present and
still tested:

- `SUPPORTED_COHORTS`, `get_cohort_percentiles(cohort)`,
  `get_matched_percentiles(data, cohort)` in `benchmark/percentile.py`
- `COHORT_LABELS` and `cohort_label()` in `config.py`, and the `CohortLabel`
  Literal in `api/models/results.py`
- the `?cohort=` and `?match=` query parameters
- the peer-matching engine in `benchmark/matching.py` — level selection,
  small-cell suppression, transparent fallback, plain-language descriptions —
  tested directly against synthetic strata tables in `tests/test_peer_matching.py`
- `data/strata_tables.py`, the reader a frozen stratified table plugs into

Registering a properly sourced cohort is therefore additive: supply a percentile
table and (optionally) a strata table, add the id and label, restore the two
frontend controls. No architectural change is required.

## 6. Conditions for registering any future cohort

1. **Written provenance in this document** — who collected the data, under what
   study or program, and the citation or agreement that permits its use.
2. **A label that names a population, not an institution**, unless that
   institution has given written permission to be named. Enforced by
   `test_no_cohort_label_claims_an_institutional_origin`.
3. **Aggregates only in the repository**, minimum cell size 30, patient rows never
   committed.
4. **Caveats stated where the numbers appear**, not only here — any deviation
   from the NHANES pipeline (fasting status, BP measurement method, clinic vs
   survey sampling) must be visible to whoever reads the percentile.

The intended next step is a published-literature reference distribution (for
example MASALA, or another South Asian cohort study with published percentiles),
which satisfies all four by construction: every number is citable.

## 7. Invariant that outlives every cohort

NHANES has no South Asian–specific sample. The NHANES cohort is therefore labeled
as what it is, is never labeled "South Asian", and South Asian ancestry is
surfaced only as a qualitative risk-enhancing factor. That proxy-vs-actual
distinction is the intellectual core of the project and is enforced by
`tests/test_cohort_registry.py`.
