"""
Browser performance suite — a lightweight, dependency-free proxy for Core Web
Vitals, not a full Lighthouse audit. There is no `lighthouse` CLI or
playwright-lighthouse wrapper in this project's toolchain, and adding one was
judged out of scope for this pass (a real CWV/Lighthouse run also wants a
non-headless, non-sandboxed, unthrottled-vs-throttled comparison that doesn't
fit this test harness). What this DOES check, using only the browser's native
Performance API (page.evaluate — no extra dependency): first-contentful-paint
stays under a generous budget, total transferred bytes stay under a sane
budget (a regression guard against bundle bloat, not a real-world figure —
headless Chromium with no cache has different numbers than a real visit), and
the console stays free of errors on load. A clean run here is a floor, not a
substitute for an actual Lighthouse/CrUX pass before a real launch.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser

# Generous on purpose: this runs in a shared, possibly-loaded headless
# sandbox, not representative end-user hardware/network. The point is to
# catch a severe regression (a runaway bundle, a page that never paints), not
# to assert a production performance budget.
_FCP_BUDGET_MS = 4000
_TRANSFER_BUDGET_BYTES = 3 * 1024 * 1024  # 3 MB


def _perf_snapshot(page) -> dict:
    return page.evaluate(
        """() => {
            const paint = performance.getEntriesByType('paint')
                .find((e) => e.name === 'first-contentful-paint');
            const resources = performance.getEntriesByType('resource');
            const transferred = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
            return { fcp: paint ? paint.startTime : null, transferred };
        }"""
    )


def _check_page(page, base_url: str, path: str, console_errors: list[str]) -> None:
    page.goto(f"{base_url}{path}", wait_until="networkidle")
    snap = _perf_snapshot(page)
    assert snap["fcp"] is not None, f"{path}: no first-contentful-paint entry recorded"
    assert snap["fcp"] < _FCP_BUDGET_MS, f"{path}: FCP {snap['fcp']:.0f}ms exceeds {_FCP_BUDGET_MS}ms budget"
    assert snap["transferred"] < _TRANSFER_BUDGET_BYTES, (
        f"{path}: transferred {snap['transferred']} bytes exceeds {_TRANSFER_BUDGET_BYTES} byte budget"
    )
    assert console_errors == [], f"{path}: console errors on load: {console_errors}"


@pytest.fixture()
def console_errors(page):
    errors: list[str] = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    yield errors


def test_home_page_performance_budget(page, base_url, console_errors):
    _check_page(page, base_url, "/", console_errors)


def test_benchmark_page_performance_budget(page, base_url, console_errors):
    _check_page(page, base_url, "/benchmark/", console_errors)


def test_timeline_page_performance_budget(page, base_url, console_errors):
    _check_page(page, base_url, "/timeline/", console_errors)
