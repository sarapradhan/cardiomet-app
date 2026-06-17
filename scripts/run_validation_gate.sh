#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; D='\033[2m'; E='\033[0m'

echo -e "\n${D}==================================================${E}"
echo " SAHC RiskLens - Validation Gate"
echo -e "${D}==================================================${E}\n"

echo "1. Test tiers (smoke -> unit -> integration -> e2e)..."
echo "   1a. Smoke..."
pytest tests/test_smoke.py -q --tb=short || { echo -e "${R}  x Smoke FAILED${E}"; exit 1; }
echo "   1b. Unit (clinical, data, benchmark)..."
pytest tests/test_thresholds.py tests/test_cohort_filters.py tests/test_missingness.py \
       tests/test_biomarker_mapping.py tests/test_percentile.py \
       tests/test_series.py tests/test_trajectory_analytics.py -q --tb=short \
  || { echo -e "${R}  x Unit FAILED${E}"; exit 1; }
echo "   1c. API + integration..."
pytest tests/test_api_endpoints.py tests/test_integration.py -q --tb=short \
  || { echo -e "${R}  x Integration FAILED${E}"; exit 1; }
echo "   1d. End-to-end (boots real server)..."
pytest tests/test_e2e.py -q --tb=short || { echo -e "${R}  x E2E FAILED${E}"; exit 1; }
echo -e "${G}  ok All test tiers passed${E}\n"

if [[ -f "frontend/package.json" && -d "frontend/node_modules" ]]; then
  echo "2. TypeScript type check..."
  (cd frontend && npm run type-check) || { echo -e "${R}  x TypeScript errors${E}"; exit 1; }
  echo -e "${G}  ok TypeScript: no errors${E}\n"
else
  echo -e "${Y}2. Skipped TypeScript (frontend deps not installed - run: cd frontend && npm install)${E}\n"
fi

echo "3. Required docs..."
for doc in docs/DATA_DICTIONARY.md docs/CLINICAL_LOGIC_APPENDIX.md \
           docs/SAFETY_AND_LIMITATIONS.md docs/VALIDATION_PLAN.md \
           docs/RELEASE_CHECKLIST.md docs/SESSION_STATUS.md docs/ARCHITECTURE.md \
           docs/E2E_CHECKLIST.md; do
  [[ -s "$doc" ]] && echo -e "${G}  ok $doc${E}" || { echo -e "${R}  x MISSING: $doc${E}"; exit 1; }
done
echo ""

echo "4. Diagnostic language scan (api/ + sahc_risklens/)..."
DIAG='you have [a-z]|you are high risk|this predicts your|you should take'
if find api/ sahc_risklens/ -name "*.py" -exec grep -inE "$DIAG" {} + 2>/dev/null | grep -v "prohibited\|phrase\|assert"; then
  echo -e "${R}  x Diagnostic language found - fix before release${E}"; exit 1
fi
echo -e "${G}  ok No diagnostic language${E}\n"

echo "5. Cohort filter check (RIDRETH3 == 6)..."
grep -rn "RIDRETH3" sahc_risklens/ --include="*.py" 2>/dev/null | grep -qE "==\s*6|ridreth3_value" && \
  echo -e "${G}  ok RIDRETH3 == 6 cohort filter present${E}" \
  || { echo -e "${R}  x RIDRETH3 == 6 filter missing${E}"; exit 1; }
echo ""

echo "6. HbA1c (LBXGH) end-to-end check..."
grep -rl "LBXGH" sahc_risklens/ --include="*.py" 2>/dev/null | grep -q . && \
  echo -e "${G}  ok LBXGH present${E}" || { echo -e "${R}  x LBXGH missing${E}"; exit 1; }
echo ""

echo "7. BP variable check (BPXSY/BPXDI - 2017-2018 auscultatory)..."
grep -rq "BPXSY1" sahc_risklens/ --include="*.py" 2>/dev/null && \
  echo -e "${G}  ok BPXSY/BPXDI present${E}" || echo -e "${Y}  ! BP variables not found in sahc_risklens/${E}"
echo ""

echo "8. Fasting filter check (PHAFSTHR >= 8)..."
grep -rq "PHAFSTHR" sahc_risklens/ --include="*.py" 2>/dev/null && \
  echo -e "${G}  ok PHAFSTHR fasting filter present${E}" || echo -e "${Y}  ! PHAFSTHR not found${E}"
echo ""


echo "9. Trajectory descriptive-only scan..."
if grep -inE "will (reach|develop)|predict|forecast|expected to|is working|lowered your|caused by" sahc_risklens/trajectory/*.py | grep -vE "emits no predictive|no predictive/causal|descriptive"; then
  echo -e "${R}  x Predictive/causal language in trajectory source${E}"; exit 1
fi
echo -e "${G}  ok Trajectory output is descriptive-only${E}"
echo ""
echo -e "${D}==================================================${E}"
echo -e "${G} Validation gate PASSED${E}"
echo -e "${D}==================================================${E}\n"
exit 0
