# SAHC RiskLens — Product Requirements Document

## 1. Summary
Responsible cardiometabolic benchmarking and physician-discussion tool for South Asian
heart health. Compares patient biomarkers against:
1. Clinical threshold categories (ACC/AHA, ADA, WHO)
2. NHANES Non-Hispanic Asian reference distributions (accurately labeled)
3. South Asian risk-enhancing context (guideline-backed discussion layer)
4. Physician discussion prompts (template-based)

Educational and discussion-supportive. Not diagnostic.

## 2. Tech Stack
| Component | Technology | Deploy |
|---|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind + Material Design 3 | Single container (Hugging Face Spaces) |
| Backend | FastAPI + Pydantic v2 + Uvicorn | Single container (Hugging Face Spaces) |
| Clinical logic | Python (sahc_risklens/) | — |
| Tests | pytest + httpx TestClient | — |

## 3. MVP Inputs
LDL-C, HDL-C, Triglycerides, Total Cholesterol (mg/dL)
Fasting Plasma Glucose (mg/dL), HbA1c (%)
Systolic BP, Diastolic BP (mm Hg), BMI (kg/m²)
Age (years), Sex (M/F), South Asian ancestry (Y/N)
Medications: BP med, cholesterol med, insulin, diabetes pills

## 4. MVP Outputs
- Threshold classification per biomarker (per CLINICAL_LOGIC_APPENDIX.md)
- NHANES Non-Hispanic Asian benchmark (percentile/distribution)
- South Asian risk-enhancing context panel
- Limitations panel (always visible)
- Physician discussion guide (template-based)
- Missing biomarker flags and medication notes

## 5. Non-Goals
Diagnosis · treatment recommendations · South Asian-specific NHANES distributions ·
LLM health coach · data storage

## 6. Data Source
NHANES 2017–2018 (suffix _J). Cohort: RIDRETH3 == 6 (Non-Hispanic Asian).
Always labeled "NHANES Non-Hispanic Asian." See DATA_DICTIONARY.md.

## 7. Physician Discussion Guide
Rule-based template, no LLM. Values substituted into fixed text.

## 8. Phased Roadmap
P0 Foundation — scaffold, docs, stubs
P1 Clinical schema — thresholds, biomarker schema, synthetic tests
P2 Data foundation — NHANES loader, cohort filter, missingness
P3 FastAPI endpoints — Pydantic models, routes, API tests
P4 Next.js frontend — form, results, Material Design components, limitations
P5 Integration + release — end-to-end, all reviewers, single-container deploy to Hugging Face Spaces

## 9. Release Gate
Ships when: all tests pass, cohort correctly labeled, HbA1c included,
limitations visible, guide template-based, no diagnostic language,
all reviewer subagents report no Blockers.
