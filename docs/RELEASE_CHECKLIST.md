# CardioMet Lens — Release Checklist
# [BLOCKER] = must resolve before proceeding.

## P0: Foundation
- [ ] Directory structure complete
- [ ] CONTRIBUTING.md with @imports
- [ ] requirements.txt pinned, frontend/package.json created
- [ ] All docs/* files created

## P1: Clinical Schema
- [ ] [BLOCKER] All threshold values match CLINICAL_LOGIC_APPENDIX.md
- [ ] [BLOCKER] HbA1c (LBXGH -> HbA1c_pct) in biomarker schema
- [ ] HDL thresholds sex-specific
- [ ] South Asian BMI = risk-context only
- [ ] All boundary tests pass
- [ ] Clinical & Safety Reviewer: no Blockers

## P2: Data Foundation
- [ ] [BLOCKER] All NHANES variable names match DATA_DICTIONARY.md
- [ ] [BLOCKER] RIDRETH3 == 6 cohort filter tested
- [ ] [BLOCKER] PHAFSTHR >= 8 fasting glucose filter tested
- [ ] BP averaged across readings 1–3
- [ ] Missingness reported, not dropped
- [ ] Data & QA Auditor: no Blockers

## P3: FastAPI Endpoints
- [ ] [BLOCKER] BenchmarkResponse complete in api/models/results.py
- [ ] [BLOCKER] frontend/src/lib/types.ts mirrors results.py field-for-field
- [ ] [BLOCKER] cohort_label is Literal["NHANES Non-Hispanic Asian"]
- [ ] [BLOCKER] disclaimer is required field, min_length=20
- [ ] All API endpoint tests pass
- [ ] Data & QA Auditor: no Blockers

## P4: Next.js Frontend
- [ ] [BLOCKER] No diagnostic language in UI
- [ ] [BLOCKER] No treatment recommendations in UI
- [ ] [BLOCKER] Limitations panel always visible
- [ ] [BLOCKER] Disclaimer always rendered from API response
- [ ] Material Design theme applied consistently
- [ ] cohort_label rendered exactly as received
- [ ] Physician guide is template text from API (not LLM)
- [ ] npm run build passes zero TypeScript errors
- [ ] Clinical & Safety Reviewer: no Blockers

## P5: Release
- [ ] [BLOCKER] bash scripts/run_validation_gate.sh exits 0
- [ ] [BLOCKER] Release Gate Reviewer: Approved
- [ ] End-to-end flow works: form -> submit -> results renders
- [ ] Demo mode works without NHANES files
- [ ] Deployed: single container to Hugging Face Spaces
