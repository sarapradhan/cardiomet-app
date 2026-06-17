# Skill: Run Validation Gate

1. Run `bash scripts/run_validation_gate.sh` — must exit 0.
2. Failing tests = fix before proceeding. Threshold and mapping failures = Blockers.
3. Invoke reviewer:
   - P1/P4/clinical change → clinical_safety_reviewer
   - P2/P3/data or test change → data_qa_auditor
   - P5 release → release_gate_reviewer
4. Convert findings to Blocker / non-Blocker action list.
5. Fix all Blockers before proceeding.
6. Update docs/RELEASE_CHECKLIST.md and docs/SESSION_STATUS.md.
