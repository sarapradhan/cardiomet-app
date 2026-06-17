# Skill: Implement Feature

1. Read docs/PRD.md — identify exact requirement.
2. Clinical thresholds involved? Verify against CLINICAL_LOGIC_APPENDIX.md. Never invent.
3. NHANES variables involved? Verify against DATA_DICTIONARY.md. Never invent.
4. API field added/changed? Update api/models/results.py AND frontend/src/lib/types.ts together.
5. Implement smallest correct version.
6. Add or update tests. Threshold change → update boundary cases.
7. Update docs if behavior changed. Threshold change → update CLINICAL_LOGIC_APPENDIX.md and code together.
8. Run `pytest tests/ -v` — must pass.
9. Run `cd frontend && npm run type-check` — must pass.
10. Summarize: what changed, tests updated, docs updated, remaining risks.
11. Update docs/SESSION_STATUS.md.
Rule: Do not expand scope beyond the requirement.
