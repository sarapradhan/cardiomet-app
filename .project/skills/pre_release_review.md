# Skill: Pre-Release Review

1. bash scripts/run_validation_gate.sh exits 0.
2. cd frontend && npm run type-check passes.
3. README.md accurate end-to-end.
4. DATA_DICTIONARY.md matches all variable names in sahc_risklens/.
5. CLINICAL_LOGIC_APPENDIX.md matches all threshold values in code.
6. SAFETY_AND_LIMITATIONS.md complete.
7. docs/RELEASE_CHECKLIST.md P5 section fully checked.
8. Invoke release_gate_reviewer subagent.
9. Fix all Blockers.
10. Produce release summary: decision, known limitations, safe to demo, must not claim, next roadmap.
