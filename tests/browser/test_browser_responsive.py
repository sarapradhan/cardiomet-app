"""
Responsive checks — the app must remain usable at a phone width with no
horizontal overflow, and key actions stay reachable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.browser

MOBILE = {"width": 375, "height": 812}   # iPhone-class


@pytest.fixture()
def mobile_page(browser, base_url):
    ctx = browser.new_context(viewport=MOBILE)
    pg = ctx.new_page()
    pg.goto(f"{base_url}/", wait_until="domcontentloaded")
    pg.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
    yield pg
    ctx.close()


def _no_horizontal_overflow(page) -> bool:
    return page.evaluate(
        "() => document.documentElement.scrollWidth <= window.innerWidth + 1")


def test_home_no_horizontal_scroll_mobile(mobile_page, base_url):
    mobile_page.goto(f"{base_url}/", wait_until="networkidle")
    assert _no_horizontal_overflow(mobile_page), "home overflows horizontally on mobile"


def test_benchmark_no_horizontal_scroll_mobile(mobile_page, base_url):
    mobile_page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    assert _no_horizontal_overflow(mobile_page), "benchmark overflows on mobile"


def test_timeline_no_horizontal_scroll_mobile(mobile_page, base_url):
    mobile_page.goto(f"{base_url}/timeline/", wait_until="networkidle")
    assert _no_horizontal_overflow(mobile_page), "timeline overflows on mobile"


def test_primary_cta_reachable_mobile(mobile_page, base_url):
    mobile_page.goto(f"{base_url}/", wait_until="networkidle")
    assert mobile_page.get_by_role("link", name="Check my labs").first.is_visible()


def test_results_no_horizontal_scroll_mobile(mobile_page, base_url):
    mobile_page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    mobile_page.get_by_placeholder("e.g. 100").fill("168")
    mobile_page.get_by_role("button", name="See My Results").click()
    mobile_page.wait_for_url("**/results/**")
    mobile_page.wait_for_load_state("networkidle")
    assert _no_horizontal_overflow(mobile_page), "results overflow on mobile"
