"""
Responsive checks — the app must remain usable at a phone width with no
horizontal overflow, and key actions stay reachable.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.browser

MOBILE = {"width": 375, "height": 812}   # iPhone-class
NARROW = {"width": 320, "height": 568}   # narrowest phone width still in use


@pytest.fixture()
def mobile_page(browser, base_url):
    ctx = browser.new_context(viewport=MOBILE)
    pg = ctx.new_page()
    pg.goto(f"{base_url}/", wait_until="domcontentloaded")
    pg.evaluate(
        "() => { try { localStorage.clear(); sessionStorage.clear(); "
        "localStorage.setItem('sahc_tour_seen_v1:home', '1'); } catch (e) {} }"
    )
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


# --- 320px --------------------------------------------------------------
# The app bar is site-wide chrome, so when it overflows it overflows every
# route. It did: 351px of content in a 320px viewport on /, /benchmark and
# /timeline alike. The suite only ever checked 375px, so nothing caught it.


@pytest.fixture()
def narrow_page(browser, base_url):
    ctx = browser.new_context(viewport=NARROW)
    pg = ctx.new_page()
    pg.goto(f"{base_url}/", wait_until="domcontentloaded")
    pg.evaluate(
        "() => { try { localStorage.clear(); sessionStorage.clear(); "
        "localStorage.setItem('sahc_tour_seen_v1:home', '1'); } catch (e) {} }"
    )
    yield pg
    ctx.close()


@pytest.mark.parametrize("path", ["/", "/benchmark/", "/timeline/"])
def test_no_horizontal_scroll_narrow(narrow_page, base_url, path):
    narrow_page.goto(f"{base_url}{path}", wait_until="networkidle")
    over = narrow_page.evaluate(
        "() => document.documentElement.scrollWidth - window.innerWidth")
    assert over <= 1, f"{path} overflows by {over}px at 320px"


def test_app_bar_stays_one_row_narrow(narrow_page, base_url):
    """The bar wrapping to two rows is the symptom that precedes overflow."""
    narrow_page.goto(f"{base_url}/", wait_until="networkidle")
    height = narrow_page.evaluate(
        "() => document.querySelector('header[role=banner]').getBoundingClientRect().height")
    assert height < 70, f"app bar wrapped to {height}px at 320px"
