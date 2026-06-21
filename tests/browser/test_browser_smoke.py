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
    assert "SAHC RiskLens" in page.content()
    expect(page.get_by_text("Understand your lab numbers")).to_be_visible()


def test_disclaimer_always_present(page, base_url):
    page.goto(f"{base_url}/", wait_until="networkidle")
    assert page.get_by_text("not a diagnosis").first.is_visible()


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
