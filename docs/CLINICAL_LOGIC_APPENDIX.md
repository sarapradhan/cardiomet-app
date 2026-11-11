# CardioMet Lens — Clinical Logic Appendix
# Authoritative threshold values. Auto-loaded via CONTRIBUTING.md @import.
# All values in sahc_risklens/clinical/thresholds.py must match this exactly.

## Guideline Currency Note (2026-11)
The ACC/AHA Cholesterol Guideline this document cited as "2018" has been
superseded by the **2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA
Guideline on the Management of Dyslipidemia** (Blumenthal RS, Morris PB,
Gaudino M, et al. *J Am Coll Cardiol*, published online March 13, 2026,
doi:10.1016/j.jacc.2025.11.016). The ADA's annual standard cited as "2024" has
likewise been superseded by **Standards of Care in Diabetes—2026**
(*Diabetes Care* 2026;49(Suppl. 1)).

What research for this update confirmed the 2026 dyslipidemia guideline
actually changed: new LDL/non-HDL/ApoB **treatment goals** by risk tier, and a
new risk-assessment tool (PREVENT-ASCVD, replacing the pooled cohort
equations). Neither applies here — this product does not set treatment goals
or predict individual risk, by design. **Not confirmed:** whether the
guideline's own tables redefine the *descriptive* LDL/TG classification bands
below, or the ApoB/Lp(a) risk-enhancer cut-points. No secondary source
reviewed stated those bands explicitly. The citation strings below were
therefore updated to the current guideline name (citing a superseded document
when a current one exists is itself stale, independent of whether any number
changed — the same reasoning that keeps "NCEP ATP III (2001)" as the correct
citation for HDL/TC below). **The numeric bands were NOT changed** and remain
pending clinician review against the new guideline's primary-source tables.
The ApoB/Lp(a) risk-enhancer thresholds specifically are left on the 2018
citation, unchanged, as that item was already flagged PENDING CLINICAL REVIEW
before this update and is intentionally not resolved here (see below).

For HbA1c/FPG: "what's new" summaries of the 2026 ADA Standards (CGM guidance,
insulin-pump criteria, type 1 screening, obesity-drug dosing, older-adult
care) did not mention a change to the diagnostic cut-points below. Believed
unchanged on that basis; not independently verified against ADA's own
Section 2 primary text.

## LDL-C (mg/dL) — 2026 ACC/AHA/Multisociety Dyslipidemia Guideline
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

## Triglycerides (mg/dL) — 2026 ACC/AHA/Multisociety Dyslipidemia Guideline
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

## HbA1c (%) — ADA Standards of Care in Diabetes—2026
| Category   | Range    |
|------------|----------|
| Normal     | < 5.7    |
| Prediabetes| 5.7–6.4  |
| Diabetes   | >= 6.5   |

## Fasting Plasma Glucose (mg/dL) — ADA Standards of Care in Diabetes—2026
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
Cross-field consistency: when both SBP and DBP are provided, SBP must exceed
DBP (systolic is always higher than diastolic for the same reading). A pair
that violates this (e.g. 110/130) is rejected with a 422, not silently
classified — see `api/models/patient.py` `BiomarkerInput._sbp_must_exceed_dbp`.
This is input validation only; it does not infer or correct which value the
user meant.

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

## South Asian ASCVD Risk Context — 2026 ACC/AHA/Multisociety Dyslipidemia Guideline
South Asian ancestry = risk-enhancing factor, carried forward from the 2018
AHA/ACC Guideline into the current (2026) guideline's general framing.
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
| LDL, TG | 2026 ACC/AHA/Multisociety Dyslipidemia Guideline |
| HDL, TC | NCEP ATP III |
| HbA1c, FPG | ADA Standards of Care in Diabetes—2026 |
| SBP, DBP | ACC/AHA 2017 High Blood Pressure Guideline |
| BMI (standard) | WHO Global Database on Body Mass Index |
| BMI (South Asian context) | WHO Expert Consultation on BMI in Asian Populations (2004) |
| South Asian ASCVD context (general) | 2026 ACC/AHA/Multisociety Dyslipidemia Guideline |
| Lp(a) risk-enhancer threshold (South Asian context item) | 2018 AHA/ACC Cholesterol Guideline (risk-enhancing factor) — PENDING CLINICAL REVIEW |

---

## Risk-Enhancing Markers (ApoB, Lp(a)) — classification-only

> **PENDING CLINICAL REVIEW.** These advanced lipid markers are **not**
> cohort-benchmarked (NHANES does not measure them); they are
> classified against guideline cut-points only and presented as guideline-
> recognized *risk-enhancing factors* (2018 AHA/ACC Cholesterol Guideline),
> especially relevant to South Asian risk. Source of truth:
> `sahc_risklens/clinical/thresholds.py` (`_APOB_TABLE`, `_LPA_TABLE`).
>
> Deliberately left on the 2018 citation as of the 2026-11 guideline-currency
> update above: the 2026 dyslipidemia guideline's confirmed changes are
> treatment-goal and risk-tool oriented, and no source reviewed in that update
> stated whether it redefines these specific risk-enhancer cut-points
> (ApoB ≥ 130 mg/dL; Lp(a) ≥ 50 mg/dL / ≥ 125 nmol/L). This status is
> unresolved engineering-side and needs an actual clinician to check the new
> guideline's tables — it is not something code changes can close out.

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
