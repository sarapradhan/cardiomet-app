"""
Browser accessibility suite — automated WCAG 2.2 AA scan via axe-core, run
against the real single-container app (same base_url/page fixtures as
test_browser_smoke.py). This complements, not replaces, the functional
Playwright suite and any manual/expert review: axe-core only flags violations
that are machine-checkable without human judgment (missing labels, contrast,
ARIA misuse, missing landmarks, etc.) — it is documented to catch roughly a
third to half of real WCAG issues by design. A clean run here is necessary,
not sufficient, for an accessibility sign-off.

Requires `axe-core` installed under frontend/node_modules (npm install in
frontend/ — package.json devDependencies). Skips cleanly if it's missing, same
pattern as conftest.py's playwright import-skip, so this never blocks a
checkout that hasn't run npm install yet.
"""
from __future__ import annotations

from pathlib import Path

import pytest

AXE_JS = Path(__file__).resolve().parents[2] / "frontend" / "node_modules" / "axe-core" / "axe.min.js"

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(not AXE_JS.exists(), reason="axe-core not installed; run npm install in frontend/"),
]

# Rules disabled with a reason, never silently. Keep this list short and
# specific — a broad disable here would hide real regressions.
_DISABLED_RULES: dict[str, str] = {
    # "region": "the illustrative hero <div> art is aria-hidden/labeled; revisit if axe still flags it",
}


def _scan(page) -> list[dict]:
    page.add_script_tag(path=str(AXE_JS))
    return page.evaluate(
        """async (disabledRules) => {
            const options = {
                runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] },
            };
            if (Object.keys(disabledRules).length) {
                options.rules = Object.fromEntries(
                    Object.keys(disabledRules).map((id) => [id, { enabled: false }])
                );
            }
            const r = await axe.run(document, options);
            return r.violations.map((v) => ({
                id: v.id,
                impact: v.impact,
                help: v.help,
                nodes: v.nodes.map((n) => n.target),
            }));
        }""",
        _DISABLED_RULES,
    )


def _assert_no_violations(page, base_url: str, path: str) -> None:
    page.goto(f"{base_url}{path}", wait_until="networkidle")
    violations = _scan(page)
    assert violations == [], f"axe-core WCAG violations on {path}: {violations}"


def test_home_page_has_no_axe_violations(page, base_url):
    _assert_no_violations(page, base_url, "/")


def test_benchmark_page_has_no_axe_violations(page, base_url):
    _assert_no_violations(page, base_url, "/benchmark/")


def test_timeline_page_has_no_axe_violations(page, base_url):
    _assert_no_violations(page, base_url, "/timeline/")


def test_results_page_has_no_axe_violations(page, base_url):
    """Results renders from sessionStorage (set by the benchmark form on
    submit) rather than a server route, so seed it directly before navigating."""
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    fake_result = {
        "threshold_results": [
            {"biomarker": "LDL", "value": 162, "unit": "mg/dL", "category": "High",
             "category_description": "High (160-189 mg/dL)",
             "guideline_source": "2026 ACC/AHA/Multisociety Dyslipidemia Guideline", "note": None},
        ],
        "risk_enhancing_markers": [],
        "benchmark_data": [
            {"biomarker": "LDL", "patient_value": 162, "cohort_p10": 80, "cohort_p25": 95,
             "cohort_median": 110, "cohort_p75": 130, "cohort_p90": 150,
             "cohort_label": "NHANES Non-Hispanic Asian", "cohort_n": 500,
             "matched": False, "match_n": None, "match_description": None},
        ],
        "south_asian_context": [],
        "physician_guide": [],
        "care_navigation": [],
        "missing_biomarkers": [],
        "medication_notes": [],
        "cohort": "nhanes_asian",
        "cohort_label": "NHANES Non-Hispanic Asian",
        "cohort_years": "2017-2018",
        "cohort_weighted": False,
        "matched": False,
        "match_description": None,
        "disclaimer": "This tool provides educational benchmarking context only.",
        "validation_status": "Phase 1 — Demo",
    }
    page.evaluate(
        "(r) => sessionStorage.setItem('benchmarkResult', JSON.stringify(r))",
        fake_result,
    )
    page.goto(f"{base_url}/results/", wait_until="networkidle")
    violations = _scan(page)
    assert violations == [], f"axe-core WCAG violations on /results/: {violations}"
