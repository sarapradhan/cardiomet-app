# CardioMet Lens — Feature Guide

A feature-by-feature description of what the app does, how each piece works, and
where it lives in the code. For exact thresholds see
[`CLINICAL_LOGIC_APPENDIX.md`](CLINICAL_LOGIC_APPENDIX.md); for the API shape see
[`API_REFERENCE.md`](API_REFERENCE.md).

---

## 1. Guideline classification

Every entered value is placed into a named guideline category — the absolute,
population-independent read.

- **Markers:** LDL, HDL (sex-specific), Triglycerides, Total Cholesterol, HbA1c,
  Fasting Glucose, Systolic/Diastolic BP, BMI.
- **Sources:** ACC/AHA 2018 (lipids), NCEP ATP III (HDL/TC), ADA 2024 (glucose/
  HbA1c), ACC/AHA 2017 (BP), WHO (BMI). Each category names its guideline.
- **Behavior:** missing values are shown as "Not provided," never imputed.
  Medication flags add a note but never change a category. BMI is dual — the
  standard WHO category here, the South Asian category in the context panel.
- **Code:** `clinical/thresholds.py` (`classify_all_biomarkers`).

## 2. Population benchmark with selectable cohorts

Shows where a value sits within a reference distribution (p10/p25/median/p75/p90)
so "high" becomes "high relative to whom, and by how much."

- **Cohorts:**
  - `nhanes_asian` — NHANES 2017–2018 Non-Hispanic Asian (a public proxy).
  - `sahc` — South Asian Heart Center clinical cohort (a genuine South Asian
    population).
- **Honest labeling:** each cohort carries its own true label; the NHANES cohort
  is never called "South Asian" (enforced by tests).
- **Source resolution:** live computation from raw data when present; otherwise a
  frozen aggregate table verified identical to the live numbers.
- **Code:** `benchmark/percentile.py`; `data/*_loader.py`, `data/*demo_cohort.py`.
- **API:** `?cohort=`. **UI:** the "Compare against" selector.

## 3. Peer matching (SCORE parity, improved)

Optionally narrows the comparison group to the patient's matched subgroup — same
sex, age band, and medication use — like the original SCORE tool.

- **Match levels (narrowest first):** sex + age + medication → sex + age → whole
  cohort.
- **Improvement over SCORE:** cells below 30 people are suppressed; the engine
  falls back transparently and discloses the peer group used (`match_description`,
  e.g. "Women, 49–64, on cholesterol medication") and its size (`match_n`).
- **Availability:** offered for the SAHC cohort; NHANES falls back to whole-cohort
  with `matched=false` (too small to stratify; raw files not shipped).
- **Code:** `benchmark/matching.py`; frozen `data/strata_tables.json`
  (regenerate via `scripts/build_strata_tables.py`).
- **API:** `?match=true`. **UI:** the "Match to people like me" toggle.

## 4. Advanced lipid markers (ApoB, Lp(a))

Markers that capture South Asian risk better than the standard panel, classified
as guideline risk-enhancing factors.

- **Classification-only:** no cohort measures them, so there is no percentile —
  just a guideline category (2018 AHA/ACC risk-enhancer thresholds: ApoB ≥130
  mg/dL; Lp(a) ≥50 mg/dL / ≥125 nmol/L).
- **Behavior:** present only when supplied (never flagged "missing"); ApoB carries
  a statin medication note; an elevated Lp(a) adds a South Asian context item.
- **Status:** thresholds marked **pending clinical review**.
- **Code:** `clinical/thresholds.py` (`classify_risk_enhancing_markers`); UI
  `RiskEnhancingMarkers.tsx`.

## 5. South Asian risk context

Qualitative, guideline-backed discussion points — never a numeric risk score.

- **Items:** ancestry as an ASCVD risk-enhancing factor (2018 AHA/ACC); South
  Asian BMI action points (WHO 2004, 23 / 27.5); elevated Lp(a) context.
- **Gating:** shown when the user reports South Asian ancestry (Lp(a) item when
  Lp(a) ≥ 50).
- **Code:** `clinical/south_asian_context.py`; UI `SouthAsianContextPanel.tsx`.

## 6. Longitudinal trajectory

Descriptive trends across multiple dated draws.

- **Reports:** direction (toward/away from the guideline-preferred range), size of
  change, per-year rate, category transitions, and observed effects around a
  medication change.
- **Boundaries:** no forecasting, no time-to-threshold, no causal attribution, no
  risk score (enforced by a descriptive-only scan).
- **Data ownership:** the user exports/imports a portable health file; nothing is
  stored server-side.
- **Code:** `trajectory/` + `POST /api/v1/trajectory`; UI `timeline/`, `Timeline.tsx`,
  `TrajectorySummary.tsx`.

## 7. Appointment preparation

- **Physician discussion guide** — template prompts for non-normal values, each
  citing its guideline (`clinical/disclaimers.py`, `PhysicianGuide.tsx`).
- **Clinician pre-visit brief** — a copy-to-clipboard summary compiled client-side
  from the response: out-of-range values + sources, advanced markers, matched-peer
  context, medications, discussion topics, missing data (`ClinicianBrief.tsx`).
- **Care navigation** — non-prescriptive next steps: family/cascade screening
  (triggered by South Asian ancestry or elevated heritable Lp(a)) and a pointer to
  the center's prevention program (`clinical/care_navigation.py`, `CareNavigation.tsx`).

## 8. Safety scaffolding (always on)

- Disclaimer rendered first; limitations panel rendered last and not collapsible.
- No LLM in the patient-facing path; all generated text is fixed templates.
- Diagnostic/predictive language scanned in CI; medication notes never alter
  classifications; small peer cells suppressed.
- See [`SAFETY_AND_LIMITATIONS.md`](SAFETY_AND_LIMITATIONS.md) and the
  CardioSafeBench safety benchmark (`cardiosafebench/`).
