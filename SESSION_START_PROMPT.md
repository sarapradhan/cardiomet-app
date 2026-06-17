# SAHC RiskLens — Session Start

Read: CONTRIBUTING.md → docs/PRD.md → docs/SESSION_STATUS.md

## Today's Task
[FILL IN — e.g., "Implement NHANES data loader and cohort filter (P2)"]

## Phase Context
[FILL IN — e.g., "P1 complete, no Blockers. Starting P2. Invoke Data & QA Auditor after loader."]

## Hard Constraints
- NHANES variables → DATA_DICTIONARY.md only
- Threshold values → CLINICAL_LOGIC_APPENDIX.md only
- API field change → update results.py AND types.ts together
- cohort_label → always "NHANES Non-Hispanic Asian"
- disclaimer → always present, always rendered in frontend

## End of Session
- [ ] `bash scripts/run_validation_gate.sh` exits 0
- [ ] `cd frontend && npm run type-check` passes
- [ ] `docs/SESSION_STATUS.md` updated
