# Session Status
_Last updated: 2026-08-09 - test inventory reconciled against a live run of the current suite_

## Phase 1 Milestone Status
| Milestone | Status | Notes |
|---|---|---|
| P0: Foundation | Complete | Scaffold + pyproject.toml pythonpath fix. |
| P1: Clinical schema | Complete | clinical/{biomarkers,thresholds,south_asian_context,disclaimers}.py + test_thresholds.py (75 tests). |
| P2: Data foundation | Complete | data/{nhanes_loader,cohort_filters,missingness,demo_cohort}.py + benchmark/percentile.py. Verified against REAL NHANES 2017-2018 files (NH-Asian cohort n=1168). 39 tests. |
| P3: FastAPI endpoints | Complete | benchmark.py + thresholds.py routers wired to P1/P2. All 17 endpoint tests pass. |
| P4: Next.js frontend | Complete | 7 MD3 components + wired pages. Type-check clean, production build 6/6 pages. Next pinned to patched 14.2.35. |
| P5: Integration + release | Complete | Smoke (38) + integration (14) + e2e (8, real uvicorn). Validation gate 8/8. Release Gate Reviewer: compliance pass. |

## Test Inventory (307 total, backend)
| Suite | Tests | Scope |
|---|---|---|
| test_smoke.py | 38 | Every module imports + entry point runs |
| test_thresholds.py | 75 | All boundary cases, sources, guide, meds, SA context |
| test_cohort_filters.py | 8 | RIDRETH3==6, fasting filter boundaries |
| test_missingness.py | 6 | Counts/pct, no imputation |
| test_biomarker_mapping.py | 9 | BP averaging, renaming + real-file checks (5 skip without local NHANES XPT files) |
| test_percentile.py | 16 | Benchmark structure, demo determinism, rank |
| test_sahc_cohort.py | 17 | SAHC cohort loading, no-crossed-labels invariant |
| test_peer_matching.py | 12 | Stratified matching, suppression, fallback |
| test_risk_enhancing_markers.py | 9 | ApoB/Lp(a) classification-only behavior |
| test_care_navigation.py | 6 | Non-prescriptive navigation language safety |
| test_series.py | 12 | Dated-draw series model + validation |
| test_trajectory_analytics.py | 24 | Direction, rate of change, transitions, descriptive-only guardrails |
| test_cardiosafebench.py | 19 | CardioSafeBench rubric + case scoring |
| test_api_endpoints.py | 17 | Endpoint contract, validation, safety |
| test_trajectory_api.py | 17 | Trajectory endpoint contract |
| test_integration.py | 14 | Cross-component consistency through API |
| test_e2e.py | 8 | Real uvicorn over HTTP, CORS, safety invariants |

**Total: 307 collected.** Pass/skip split depends on whether local NHANES/SAHC raw data files are present (gitignored, not committed): with no local data, 302 pass and 5 skip (all in `test_biomarker_mapping.py`, which needs the real XPT files); with local data present, all 307 run and some real-data-only assertions that otherwise no-op will execute instead. Either way, 307 is the number that should appear anywhere this suite is cited — re-verify with `python -m pytest tests/ -q --ignore=tests/browser` before updating.

Separately, a **23-test Playwright browser tier** exists in `tests/browser/` (10 e2e + 5 responsive + 8 smoke), which requires a built frontend (`cd frontend && npm run build`) and Playwright browsers installed; it is not included in the 307 figure above.

## Critical Accuracy Fixes (against real NHANES data)
- Downloader URLs corrected to current CDC DataFiles scheme + XPORT validation (old path served HTML 404s).
- DATA_DICTIONARY: BP variables are BPXSY1-3/BPXDI1-3 (auscultatory, 2017-2018), NOT BPXOSY*/BPXODI* (2021+). PHAFSTHR is in FASTQX_J, not GLU_J.
- Demo cohort percentiles ARE the real NH-Asian percentiles; live vs demo verified identical across all 9 biomarkers.

## API Contract Sync
results.py <-> types.ts: In sync. No schema changes in P2-P5 (only router wiring + frontend consumption).

## Subagent Review Status
| Reviewer | Last Invoked | Outcome | Open Blockers |
|---|---|---|---|
| Clinical & Safety Reviewer | After P1 | Approved w/ non-blocking (1 Medium fixed) | None |
| Data & QA Auditor | After P2/P3 | Variable names verified against real files; BP/fasting corrected | None |
| Release Gate Reviewer | After P5 | Compliance pass (Literal cohort_label, required disclaimer, no-LLM guide, limitations always shown, no diagnostic language) | None |

## Open Issues
- npm audit: remaining high items require Next 16 (breaking) - deferred.
- starlette TestClient deprecation warning (cosmetic) - httpx2 migration pending.

## Next Session Start Point
The core app is functionally complete and deployed. Next actions:
1. Deploy: single container to Hugging Face Spaces (set NEXT_PUBLIC_API_URL + ALLOWED_ORIGINS as needed).
2. Run docs/E2E_CHECKLIST.md Tier 2 (browser) against the deployed Space.


## Trajectory Tracking — T0/T1 (Clinical Core) — COMPLETE
_Added: longitudinal trajectory tracking, the differentiation capability (see docs/INCREMENTAL_VALUE_SPEC.md)._

| Phase | Status | Notes |
|---|---|---|
| T0: Data model | Complete | sahc_risklens/trajectory/{series,health_file}.py. Dated draws, immutable date-sorted series, user-owned portable health file (no server storage). 12 tests. |
| T1: Analytics engine | Complete | sahc_risklens/trajectory/analytics.py. Direction, change, per-year rate, category transitions, intervention detection. Reuses clinical core (classify_all_biomarkers, medication_affects()); zero new thresholds. 24 tests incl. descriptive-only guardrails. |
| T2: API endpoint | Complete | POST /api/v1/trajectory (stateless). api/models/{series,trajectory}.py + router. 17 tests; contract mirrored to types.ts. |
| T3: Frontend timeline | Complete | /timeline page, Timeline (SVG small-multiples) + TrajectorySummary components, healthFile export/import (user-owned, no server storage). Type-check + build pass (7/7 pages). |
| T4: Gate/review/docs | Partial | gate+smoke+e2e cover trajectory; ARCHITECTURE.md update + browser walkthrough remain |

Methodology: design-first (PRD + technical design), TDD (tests written first, red->green), three persona reviews (Staff Engineer, Data & QA Auditor, Clinical & Safety Reviewer) — all PASS, no Blockers. See docs/trajectory/BUILD_LOG_T0_T1.md and docs/trajectory/BUILD_LOG_T2_T3.md for the point-in-time test counts recorded during that work (184 → 220 → 243); the SAHC-cohort/peer-matching/ApoB-Lp(a)/CardioSafeBench batch that shipped afterward brought the suite to its current 307. Additive public accessors added to clinical core (thresholds.medication_affects, disclaimers.medication_labels) to keep the medication map single-source; no regressions.
