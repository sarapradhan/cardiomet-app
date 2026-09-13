"""
Browser smoke suite — fast checks that every page loads and renders its key
landmarks. Drives the real single-container app (UI + API on one origin).
"""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser


def test_home_loads(page, base_url):
    page.goto(f"{base_url}/", wait_until="networkidle")
    assert "CardioMet Lens" in page.content()
    expect(page.get_by_role("heading", name="Context before conclusions.")).to_be_visible()


def test_disclaimer_always_present(page, base_url):
    page.goto(f"{base_url}/", wait_until="networkidle")
    assert page.get_by_text("not a diagnosis").first.is_visible()


def test_home_sections_present(page, base_url):
    """The ported home page's argument, section by section."""
    page.goto(f"{base_url}/", wait_until="networkidle")
    for heading in [
        "A lab report gives you numbers. It rarely gives you a place to begin.",
        "From lab panel to better prepared.",
        "The difference is in the detail it refuses to hide.",
        "One tool. Two perspectives that belong in the same conversation.",
        "A complete picture. Deliberate limits.",
    ]:
        expect(page.get_by_role("heading", name=heading)).to_be_visible()


def test_home_states_its_limits(page, base_url):
    """The out-of-scope list is a load-bearing claim, not decoration."""
    page.goto(f"{base_url}/", wait_until="networkidle")
    body = page.inner_text("body").lower()
    for phrase in ["diagnosis", "individual risk", "treatment recommendation"]:
        assert phrase in body, f"home page no longer states it avoids {phrase!r}"


def test_home_names_only_registered_cohorts(page, base_url):
    """The 'sahc' cohort was removed as unsourced; the home page must not sell it.

    Guards the port: the standalone marketing page this came from named a
    'South Asian Heart Center clinical cohort' as a second selectable cohort,
    which no longer exists. South Asian *guideline context* is a separate thing
    and is still legitimately described.
    """
    page.goto(f"{base_url}/", wait_until="networkidle")
    body = page.inner_text("body")
    assert "South Asian Heart Center" not in body
    assert "NHANES Non-Hispanic Asian" in body


def test_legend_renders(page, base_url):
    page.goto(f"{base_url}/", wait_until="networkidle")
    for label in ["In range", "Elevated", "High", "Not provided"]:
        assert page.get_by_text(label, exact=True).first.is_visible()
    for panel in ["Lipids", "Glucose", "Blood pressure", "Body"]:
        assert page.get_by_text(panel, exact=True).first.is_visible()


def test_nav_to_benchmark(page, base_url):
    page.goto(f"{base_url}/", wait_until="networkidle")
    page.get_by_role("link", name="Check my labs").first.click()
    page.wait_for_url("**/benchmark/**")
    expect(page.get_by_text("Enter Your Lab Values")).to_be_visible()


def test_benchmark_page_loads(page, base_url):
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    assert page.get_by_text("Lipids").first.is_visible()
    expect(page.get_by_role("button", name="See My Results")).to_be_visible()


def test_timeline_page_loads(page, base_url):
    page.goto(f"{base_url}/timeline/", wait_until="networkidle")
    expect(page.get_by_text("Your Cardiometabolic Timeline")).to_be_visible()


def test_skip_link_present(page, base_url):
    page.goto(f"{base_url}/", wait_until="networkidle")
    assert page.get_by_role("link", name="Skip to content").count() == 1


def test_api_reachable_same_origin(page, base_url):
    """The UI's origin also serves the API (single container)."""
    resp = page.request.get(f"{base_url}/health")
    assert resp.status == 200
    assert resp.json()["status"] == "ok"
