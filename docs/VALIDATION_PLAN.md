# SAHC RiskLens — Validation Plan

## Principle
Validation precedes features. Every threshold value, variable mapping, and data
transformation is tested before the UI is considered complete.

## Layer 1 — Unit Tests (Python)
test_thresholds.py — boundary cases for every biomarker in CLINICAL_LOGIC_APPENDIX.md:
  LDL: 99,100,129,130,159,160,189,190
  HDL male: 39,40,59,60 | HDL female: 49,50,59,60
  TG: 149,150,199,200,499,500 | TC: 199,200,239,240
  HbA1c: 5.69,5.7,6.4,6.49,6.5 | FPG: 99,100,125,126
  SBP: 119,120,129,130,139,140 | DBP: 79,80,89,90
  BMI standard: 18.4,18.5,24.9,25.0,29.9,30.0
  BMI South Asian: 22.9,23.0,27.4,27.5

test_biomarker_mapping.py — all DATA_DICTIONARY.md variables present after loading
test_cohort_filters.py — RIDRETH3==6 filter correctness
test_missingness.py — missing values reported, not silently dropped

## Layer 2 — Integration Tests
test_synthetic_cases.py — 9 fixtures from conftest.py
test_api_endpoints.py — threshold correctness, cohort_label, disclaimer, safety, input validation

## Layer 3 — Subagent Reviews
P1 → Clinical & Safety Reviewer
P2/P3 → Data & QA Auditor
P4 → Clinical & Safety Reviewer
P5 → Release Gate Reviewer
Before any AI feature is added to the patient-facing path → all three reviewers

## Release Criteria
run_validation_gate.sh exits 0 · npm run type-check passes ·
all boundary tests pass · all 9 synthetic cases pass · all API endpoint tests pass ·
no Blockers from any reviewer
