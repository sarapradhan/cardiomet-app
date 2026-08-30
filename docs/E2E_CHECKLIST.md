# CardioMet Lens - End-to-End Checklist

Two tiers of end-to-end verification:

## Tier 1 - API end-to-end (automated)
`tests/test_e2e.py` boots a real uvicorn server and drives it over HTTP. Run:
```bash
pytest tests/test_e2e.py -v
```
Covers: server boot + health, full benchmark contract over the wire, safety
invariants (cohort_label, disclaimer, no diagnostic language), clinical
correctness, /thresholds, input validation (422), CORS header for the frontend
origin.

## Tier 2 - Browser end-to-end (manual, or CI with Playwright)
Run backend and frontend, then walk the flow:
```bash
# Terminal 1
uvicorn api.main:app --reload                     # http://localhost:8000
# Terminal 2
cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Checklist:
- [ ] Home page renders; the educational-only banner is visible at the top.
- [ ] "Start Benchmark" navigates to /benchmark.
- [ ] Form accepts partial input (leave several fields blank).
- [ ] South Asian ancestry checkbox and medication checkboxes toggle.
- [ ] Submitting navigates to /results and renders cards.
- [ ] Disclaimer banner shows at the top of results, verbatim from the API.
- [ ] cohort_label chip reads exactly "NHANES Non-Hispanic Asian".
- [ ] Threshold cards show categories; blank inputs render a muted "Not provided" chip.
- [ ] Distribution chart shows percentile bands; your value marker appears for provided biomarkers.
- [ ] South Asian context panel appears only when ancestry is checked.
- [ ] Medication notes appear only when a medication is checked.
- [ ] Physician guide lists only non-normal biomarkers; empty state shows for an all-normal patient.
- [ ] Limitations panel is always visible and cannot be collapsed away.
- [ ] Reloading /results directly with no session shows the "no results" empty state.
- [ ] Refreshing after submit: result persists for the tab session, clears on tab close (sessionStorage).
- [ ] Keyboard: all inputs and buttons reachable by Tab; focus is visible.
- [ ] Mobile width (375px): layout remains usable, no horizontal scroll.

## Production build check (automated)
```bash
cd frontend && npm run type-check && NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build
```
Expect: type-check clean, build generates all pages with no errors.
