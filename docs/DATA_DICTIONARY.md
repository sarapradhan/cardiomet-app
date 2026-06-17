# SAHC RiskLens — Data Dictionary
# Authoritative NHANES variable reference. Auto-loaded via CONTRIBUTING.md @import.
# All variable names in sahc_risklens/ must match this document exactly.
#
# VERIFIED against the real NHANES 2017-2018 (_J) public XPT files on 2026-06-13.
# Two corrections from the original draft, confirmed against downloaded data:
#   1. Blood pressure in 2017-2018 uses AUSCULTATORY variables BPXSY1-3 / BPXDI1-3
#      (the oscillometric BPXOSY*/BPXODI* names belong to the 2021+ cycle).
#   2. Fasting duration PHAFSTHR lives in the FASTQX_J file, not GLU_J.

## NHANES Cycles
| Cycle | Years | Suffix | Weight |
|---|---|---|---|
| J | 2017-2018 | _J | WTMEC2YR |
| I | 2015-2016 | _I | WTMEC2YR |
| Pooled | 2015-2020 | both | WTMEC4YR |
Primary: 2017-2018 (_J).

## Cohort Filter
```python
# RIDRETH3: 1=Mexican American 2=Other Hispanic 3=Non-Hispanic White
#           4=Non-Hispanic Black 6=Non-Hispanic Asian 7=Other/Multiracial
cohort = demo_df[demo_df["RIDRETH3"] == 6].copy()
# Always label: "NHANES Non-Hispanic Asian"
```

## Variable Mapping
| File     | Variable   | Label                   | Units    | Notes                        |
|----------|------------|-------------------------|----------|------------------------------|
| DEMO_J   | SEQN       | Sequence number         | -        | Join key across all files    |
| DEMO_J   | RIDAGEYR   | Age                     | years    |                              |
| DEMO_J   | RIAGENDR   | Sex                     | 1=M 2=F  |                              |
| DEMO_J   | RIDRETH3   | Race/ethnicity          | 6=NHAsian| Cohort filter                |
| DEMO_J   | WTMEC2YR   | Survey weight (2-yr)    | -        | Required for weighted stats  |
| TCHOL_J  | LBXTC      | Total Cholesterol       | mg/dL    |                              |
| HDL_J    | LBDHDD     | HDL-Cholesterol         | mg/dL    | Direct measurement           |
| TRIGLY_J | LBDLDL     | LDL-Cholesterol         | mg/dL    | Direct in 2017-2018; fasting subsample |
| TRIGLY_J | LBXTR      | Triglycerides           | mg/dL    | Fasting subsample            |
| GHB_J    | LBXGH      | HbA1c                   | %        | Required for MVP             |
| GLU_J    | LBXGLU     | Fasting Plasma Glucose  | mg/dL    | Morning fasting subsample    |
| FASTQX_J | PHAFSTHR   | Total hours fasted      | hours    | Filter: >= 8; join on SEQN   |
| BPX_J    | BPXSY1     | Systolic BP reading 1   | mm Hg    | Average with 2 and 3         |
| BPX_J    | BPXSY2     | Systolic BP reading 2   | mm Hg    |                              |
| BPX_J    | BPXSY3     | Systolic BP reading 3   | mm Hg    |                              |
| BPX_J    | BPXDI1     | Diastolic BP reading 1  | mm Hg    | Average with 2 and 3         |
| BPX_J    | BPXDI2     | Diastolic BP reading 2  | mm Hg    |                              |
| BPX_J    | BPXDI3     | Diastolic BP reading 3  | mm Hg    |                              |
| BMX_J    | BMXBMI     | BMI                     | kg/m^2   |                              |
| BPQ_J    | BPQ050A    | Taking BP medication    | 1=Y 2=N  |                              |
| BPQ_J    | BPQ090D    | Told to take chol med   | 1=Y 2=N  |                              |
| DIQ_J    | DIQ050     | Taking insulin now      | 1=Y 2=N  |                              |
| DIQ_J    | DIQ070     | Taking DM pills         | 1=Y 2=N  |                              |

## File-to-Variable Summary (for the loader)
| File     | Pulls                                  | Join |
|----------|----------------------------------------|------|
| DEMO_J   | RIDAGEYR, RIAGENDR, RIDRETH3, WTMEC2YR | SEQN (base) |
| TCHOL_J  | LBXTC                                  | SEQN |
| HDL_J    | LBDHDD                                 | SEQN |
| TRIGLY_J | LBDLDL, LBXTR                          | SEQN |
| GHB_J    | LBXGH                                  | SEQN |
| GLU_J    | LBXGLU                                 | SEQN |
| FASTQX_J | PHAFSTHR                               | SEQN |
| BPX_J    | BPXSY1-3, BPXDI1-3                     | SEQN |
| BMX_J    | BMXBMI                                 | SEQN |
| BPQ_J    | BPQ050A, BPQ090D                       | SEQN |
| DIQ_J    | DIQ050, DIQ070                         | SEQN |

## Computed Variables
| Variable  | Formula                            | Sources        |
|-----------|------------------------------------|----------------|
| SBP_mean  | mean(BPXSY1-3), ignoring NaN       | BPXSY1/2/3     |
| DBP_mean  | mean(BPXDI1-3), ignoring NaN       | BPXDI1/2/3     |

## Filters
Fasting glucose (join FASTQX_J on SEQN, then filter):
```python
merged = glu_df.merge(fastqx_df[["SEQN", "PHAFSTHR"]], on="SEQN", how="left")
fasting = merged[merged["PHAFSTHR"] >= 8].copy()
```
BP averaging:
```python
df["SBP_mean"] = df[["BPXSY1", "BPXSY2", "BPXSY3"]].mean(axis=1)
df["DBP_mean"] = df[["BPXDI1", "BPXDI2", "BPXDI3"]].mean(axis=1)
```
Missingness: report all missing values - do not silently drop or impute.

## Internal Biomarker Keys
The loader maps NHANES variables to these internal benchmark keys (used by
sahc_risklens/benchmark/percentile.py and matched to ThresholdResult.biomarker):
| Internal key | NHANES source           |
|--------------|-------------------------|
| LDL          | LBDLDL                  |
| HDL          | LBDHDD                  |
| TG           | LBXTR                   |
| TC           | LBXTC                   |
| HbA1c        | LBXGH                   |
| FPG          | LBXGLU (fasting only)   |
| SBP          | SBP_mean (BPXSY1-3)     |
| DBP          | DBP_mean (BPXDI1-3)     |
| BMI          | BMXBMI                  |
