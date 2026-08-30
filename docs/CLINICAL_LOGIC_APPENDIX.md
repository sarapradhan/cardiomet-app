# CardioMet Lens — Clinical Logic Appendix
# Authoritative threshold values. Auto-loaded via CONTRIBUTING.md @import.
# All values in sahc_risklens/clinical/thresholds.py must match this exactly.

## LDL-C (mg/dL) — ACC/AHA 2018 Cholesterol Guideline
| Category      | Range   |
|---------------|---------|
| Optimal       | < 100   |
| Near Optimal  | 100–129 |
| Borderline High| 130–159|
| High          | 160–189 |
| Very High     | >= 190  |

## HDL-C (mg/dL) — NCEP ATP III (sex-specific)
| Category  | Male   | Female |
|-----------|--------|--------|
| Low       | < 40   | < 50   |
| Normal    | 40–59  | 50–59  |
| Protective| >= 60  | >= 60  |

## Triglycerides (mg/dL) — ACC/AHA 2018
| Category      | Range   |
|---------------|---------|
| Normal        | < 150   |
| Borderline High| 150–199|
| High          | 200–499 |
| Very High     | >= 500  |

## Total Cholesterol (mg/dL) — NCEP ATP III
| Category      | Range   |
|---------------|---------|
| Desirable     | < 200   |
| Borderline High| 200–239|
| High          | >= 240  |

## HbA1c (%) — ADA Standards of Medical Care 2024
| Category   | Range    |
|------------|----------|
| Normal     | < 5.7    |
| Prediabetes| 5.7–6.4  |
| Diabetes   | >= 6.5   |

## Fasting Plasma Glucose (mg/dL) — ADA 2024
| Category         | Range   |
|------------------|---------|
| Normal           | < 100   |
| Prediabetes (IFG)| 100–125 |
| Diabetes         | >= 126  |
Requires PHAFSTHR >= 8. Do not classify non-fasting values.
Enforced in code via `BiomarkerInput.fasting_status` (`api/models/patient.py`):
`classify_all_biomarkers` (`sahc_risklens/clinical/thresholds.py`) only applies
this table when `fasting_status == "confirmed"`. Missing / `"unknown"` /
`"not_fasting"` all return `category: None` with an explanatory
`category_description` instead of a category — default-deny, not default-allow.

## Systolic BP (mm Hg) — ACC/AHA 2017 HTN Guideline
| Category             | Range   |
|----------------------|---------|
| Normal               | < 120   |
| Elevated             | 120–129 |
| Stage 1 Hypertension | 130–139 |
| Stage 2 Hypertension | >= 140  |

## Diastolic BP (mm Hg) — ACC/AHA 2017
| Category             | Range |
|----------------------|-------|
| Normal               | < 80  |
| Stage 1 Hypertension | 80–89 |
| Stage 2 Hypertension | >= 90 |
Classification: use the higher of SBP and DBP categories.

## BMI — Standard WHO (kg/m²)
| Category    | Range      |
|-------------|------------|
| Underweight | < 18.5     |
| Normal      | 18.5–24.9  |
| Overweight  | 25–29.9    |
| Obese       | >= 30      |

## BMI — South Asian Context (kg/m²) — WHO Expert Consultation 2004
| Category       | Range     |
|----------------|-----------|
| Normal         | < 23      |
| Increased risk | 23–27.4   |
| High risk      | >= 27.5   |
Display rule: always labeled "South Asian context" — never shown as NHANES benchmark.
Always shown alongside standard WHO categories.

## South Asian ASCVD Risk Context — AHA/ACC 2018 + ACC Review
South Asian ancestry = risk-enhancing factor in 2018 AHA/ACC Guideline.
Display in South Asian context panel when south_asian == True.
Label: "guideline-based clinical context for discussion with your physician."
Do not quantify individual risk — qualitative risk-enhancing factor only.

## Medication Notes
When medication flags True, display:
"Note: You indicated you are taking [type]. Your [biomarker] may reflect medication
effects. Discuss interpretation with your clinician."
Do not adjust threshold classifications based on medication in Phase 1.

## Guideline Source Citation Strings
The section headers above are short labels for this document. The strings below are
the canonical `guideline_source` values returned in API responses (ThresholdResult,
ThresholdCategory) — sahc_risklens/clinical/thresholds.py is the source of truth for
these exact strings. Both refer to the same underlying guidelines; the strings below
are simply the fuller citation form.

| Biomarker group | guideline_source string |
|---|---|
| LDL, TG | ACC/AHA 2018 Cholesterol Guideline |
| HDL, TC | NCEP ATP III |
| HbA1c, FPG | ADA Standards of Medical Care 2024 |
| SBP, DBP | ACC/AHA 2017 High Blood Pressure Guideline |
| BMI (standard) | WHO Global Database on Body Mass Index |
| BMI (South Asian context) | WHO Expert Consultation on BMI in Asian Populations (2004) |
| South Asian ASCVD context | 2018 AHA/ACC Cholesterol Guideline |

---

## Risk-Enhancing Markers (ApoB, Lp(a)) — classification-only

> **PENDING CLINICAL REVIEW.** These advanced lipid markers are **not**
> cohort-benchmarked (the NHANES and SAHC cohorts do not measure them); they are
> classified against guideline cut-points only and presented as guideline-
> recognized *risk-enhancing factors* (2018 AHA/ACC Cholesterol Guideline),
> especially relevant to South Asian risk. Source of truth:
> `sahc_risklens/clinical/thresholds.py` (`_APOB_TABLE`, `_LPA_TABLE`).

**ApoB (mg/dL)** — 2018 AHA/ACC (risk-enhancer ≥ 130 mg/dL)

| Lower bound | Category | Range |
|---|---|---|
| — | Within range | < 90 mg/dL |
| 90 | Borderline | 90–129 mg/dL |
| 130 | High (risk-enhancing) | ≥ 130 mg/dL |

**Lp(a) (mg/dL)** — 2018 AHA/ACC (risk-enhancer ≥ 50 mg/dL / ≥ 125 nmol/L)

| Lower bound | Category | Range |
|---|---|---|
| — | Within range | < 30 mg/dL |
| 30 | Borderline | 30–49 mg/dL |
| 50 | High (risk-enhancing) | ≥ 50 mg/dL (≥ 125 nmol/L) |

Notes: ApoB carries a medication note when a cholesterol medication is flagged
(statins lower ApoB). Lp(a) is largely genetically determined and not statin-
modifiable, so it carries no medication note. Lp(a) is commonly reported in
nmol/L; this tool accepts mg/dL — clinicians should confirm units. An Lp(a)
≥ 50 mg/dL additionally surfaces a South Asian context item.
