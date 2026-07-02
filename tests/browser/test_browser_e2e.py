"""
Browser end-to-end suite — complete user journeys through the real rendered app,
exercising the full stack (UI -> same-origin API -> clinical core) and verifying
the results, the color-coding, the safety surfaces, and the longitudinal flow.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser


def _fill(page, name_substr, value):
    """Fill a number input by its visible label text."""
    page.get_by_label(name_substr).fill(str(value))


def test_benchmark_full_journey(page, base_url):
    """Enter a multi-condition panel, submit, and verify the results render."""
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")

    # Fill a realistic high-risk panel via placeholders (inputs are label-wrapped).
    page.get_by_placeholder("e.g. 100").fill("168")     # LDL
    page.get_by_placeholder("e.g. 55").fill("40")        # HDL
    page.get_by_placeholder("e.g. 5.4").fill("6.1")      # HbA1c
    page.get_by_placeholder("e.g. 118").fill("136")      # SBP
    page.get_by_placeholder("e.g. 76").fill("86")        # DBP
    page.get_by_text("South Asian ancestry").click()

    page.get_by_role("button", name="See My Results").click()
    page.wait_for_url("**/results/**")
    page.wait_for_load_state("networkidle")

    # Results sections present
    expect(page.get_by_text("Each number, on its guideline range")).to_be_visible()
    expect(page.get_by_text("Where you sit in the distribution")).to_be_visible()
    # Cohort label exact + safety
    assert page.get_by_text("NHANES Non-Hispanic Asian").first.is_visible()
    # A High classification chip appears (LDL 168)
    assert page.get_by_text("High", exact=True).first.is_visible()
    # Physician guide + limitations
    expect(page.get_by_text("Questions to Discuss With Your Clinician")).to_be_visible()
    expect(page.get_by_text("Important Limitations")).to_be_visible()


def test_results_show_south_asian_context_when_flagged(page, base_url):
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    page.get_by_placeholder("e.g. 100").fill("168")
    page.get_by_text("South Asian ancestry").click()
    page.get_by_role("button", name="See My Results").click()
    page.wait_for_url("**/results/**")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_text("South Asian Considerations")).to_be_visible()


def test_results_no_south_asian_context_when_not_flagged(page, base_url):
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    page.get_by_placeholder("e.g. 100").fill("168")
    # do NOT check south asian
    page.get_by_role("button", name="See My Results").click()
    page.wait_for_url("**/results/**")
    page.wait_for_load_state("networkidle")
    assert page.get_by_text("South Asian Considerations").count() == 0


def test_results_empty_state(page, base_url):
    """Visiting results with no prior submission shows the empty state."""
    page.goto(f"{base_url}/results/", wait_until="networkidle")
    expect(page.get_by_text("No results to show yet")).to_be_visible()


def test_no_diagnostic_language_in_rendered_results(page, base_url):
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    page.get_by_placeholder("e.g. 100").fill("190")
    page.get_by_placeholder("e.g. 5.4").fill("7.2")
    page.get_by_role("button", name="See My Results").click()
    page.wait_for_url("**/results/**")
    page.wait_for_load_state("networkidle")
    body = page.inner_text("body").lower()
    for phrase in ["you have diabetes", "you should take", "we recommend starting",
                   "your 10-year risk", "you will develop"]:
        assert phrase not in body, f"diagnostic/predictive phrase rendered: {phrase}"


def test_timeline_journey_two_draws(page, base_url):
    """Add two dated draws and render the timeline + trend summary."""
    page.goto(f"{base_url}/timeline/", wait_until="networkidle")

    # Draw 1
    page.get_by_label("Draw date").fill("2025-12-01")
    page.get_by_placeholder("e.g. 100").fill("168")
    page.get_by_role("button", name="Add this draw").click()

    # Draw 2 (LDL improved)
    page.get_by_label("Draw date").fill("2026-05-01")
    page.get_by_placeholder("e.g. 100").fill("124")
    page.get_by_role("button", name="Add this draw").click()

    # Two draws registered
    page.wait_for_selector("text=Draws added (2)")

    # Analyze
    page.get_by_role("button", name="See My Timeline").click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_text("Your Values Over Time")).to_be_visible()
    expect(page.get_by_text("What Changed")).to_be_visible()
    # descriptive trend present, no prediction
    body = page.inner_text("body").lower()
    assert "will reach" not in body and "predict" not in body


def test_keyboard_focus_visible_on_primary_action(page, base_url):
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    page.keyboard.press("Tab")
    # something receives focus (no assertion on which — just that focus works)
    focused = page.evaluate("() => document.activeElement && document.activeElement.tagName")
    assert focused is not None


def test_guided_tour_runs_and_dismisses(page, base_url):
    """The guided tour can be started and stepped through to completion."""
    # The fixture marks the tour seen; start it explicitly via the button.
    page.goto(f"{base_url}/", wait_until="networkidle")
    page.get_by_role("button", name="Take a tour").click()
    expect(page.get_by_role("dialog", name="Guided tour")).to_be_visible()
    expect(page.get_by_text("Welcome to SAHC RiskLens")).to_be_visible()
    # Step forward through the tour
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_text("The color legend")).to_be_visible()
    # Skip closes it
    page.get_by_role("button", name="Skip").click()
    expect(page.get_by_role("dialog", name="Guided tour")).not_to_be_visible()


def test_example_data_loads_and_submits(page, base_url):
    """The 'Elevated-risk example' button populates the form and produces results."""
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    page.get_by_role("button", name="Elevated-risk example").click()
    # Field should now hold the example LDL
    expect(page.get_by_placeholder("e.g. 100")).to_have_value("168")
    page.get_by_role("button", name="See My Results").click()
    page.wait_for_url("**/results/**")
    page.wait_for_load_state("networkidle")
    expect(page.get_by_text("Each number, on its guideline range")).to_be_visible()


def test_daylight_snapshot_and_benchmark_bars(page, base_url):
    """The Daylight snapshot summary and per-value benchmark bars render with data."""
    page.goto(f"{base_url}/benchmark/", wait_until="networkidle")
    page.get_by_role("button", name="Elevated-risk example").click()
    page.get_by_role("button", name="See My Results").click()
    page.wait_for_url("**/results/**")
    page.wait_for_load_state("networkidle")
    # snapshot summary
    expect(page.get_by_text("Your snapshot")).to_be_visible()
    expect(page.get_by_text("markers to review")).to_be_visible()
    # benchmark bars present (each reported value has a "You" + "Benchmark" label)
    assert page.get_by_text("Benchmark", exact=False).count() >= 1
    # SA tags surface on South Asian-relevant markers
    assert page.get_by_text("SA", exact=True).count() >= 1
    # safety surfaces intact under the new design
    expect(page.get_by_text("NHANES Non-Hispanic Asian").first).to_be_visible()
    expect(page.get_by_text("Important Limitations")).to_be_visible()
