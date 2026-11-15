"""
Browser security/robustness suite — drives the real "import health file" flow
(frontend/src/lib/healthFile.ts via the timeline page's hidden file input)
with adversarial input: malformed JSON, a structurally invalid-but-parseable
draws array, an oversized file, and an XSS payload in a free-text field. None
of this was covered by an automated test before (an external review correctly
flagged "untested" here) — this suite is the regression guard that import
path now has.
"""
from __future__ import annotations

import json

import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.browser


def _import(page, base_url, tmp_path, name: str, content: bytes):
    page.goto(f"{base_url}/timeline/", wait_until="networkidle")
    f = tmp_path / name
    f.write_bytes(content)
    page.locator('input[type="file"]').first.set_input_files(str(f))


def test_malformed_json_shows_friendly_error_not_crash(page, base_url, tmp_path):
    _import(page, base_url, tmp_path, "bad.json", b"{not valid json at all")
    expect(page.get_by_text("That file is not valid JSON.")).to_be_visible()
    # Page must still be fully functional afterward — not wedged.
    expect(page.get_by_role("heading", name="Your Cardiometabolic Timeline")).to_be_visible()


def test_missing_schema_version_rejected(page, base_url, tmp_path):
    doc = {"series": {"draws": [{"draw_date": "2025-01-01", "values": {}}]}}
    _import(page, base_url, tmp_path, "noversion.json", json.dumps(doc).encode())
    expect(page.get_by_text("Unsupported or missing health-file version.")).to_be_visible()


def test_malformed_draw_entries_rejected(page, base_url, tmp_path):
    """Regression test for the structural check added to parseHealthFile:
    before it, a draws array of arbitrary garbage objects passed straight
    through to React state with no validation at all."""
    doc = {
        "schema_version": "1.0",
        "exported_at": "2025-01-01T00:00:00Z",
        "series": {"draws": [{"not_a_draw": True}, "also not a draw", 42]},
    }
    _import(page, base_url, tmp_path, "malformed_draws.json", json.dumps(doc).encode())
    expect(page.get_by_text("Health file contains a malformed draw entry.")).to_be_visible()


def test_empty_draws_array_rejected(page, base_url, tmp_path):
    doc = {"schema_version": "1.0", "exported_at": "2025-01-01T00:00:00Z", "series": {"draws": []}}
    _import(page, base_url, tmp_path, "empty.json", json.dumps(doc).encode())
    expect(page.get_by_text("Health file contains no draws.")).to_be_visible()


def test_oversized_file_rejected_before_parsing(page, base_url, tmp_path):
    """A file over the 5MB cap (frontend/src/app/timeline/page.tsx
    MAX_HEALTH_FILE_BYTES) must be rejected by file.size before JSON.parse
    ever runs on it — padding, not a huge valid draws array, so this stays
    fast regardless of whether the cap holds."""
    oversized = b"{" + b" " * (6 * 1024 * 1024) + b'"schema_version": "1.0"}'
    _import(page, base_url, tmp_path, "huge.json", oversized)
    expect(page.get_by_text("too large", exact=False)).to_be_visible()


def test_valid_file_at_cap_boundary_is_accepted(page, base_url, tmp_path):
    """Sanity check the cap isn't accidentally rejecting legitimate files:
    a well-formed, small health file must still import normally."""
    doc = {
        "schema_version": "1.0",
        "exported_at": "2025-01-01T00:00:00Z",
        "series": {"draws": [{"draw_date": "2025-01-01", "label": "baseline",
                               "values": {"LDL_mgdl": 120, "sex": "M"}}]},
    }
    _import(page, base_url, tmp_path, "valid.json", json.dumps(doc).encode())
    expect(page.get_by_text("2025-01-01")).to_be_visible()


def test_xss_payload_in_label_renders_as_literal_text(page, base_url, tmp_path):
    """A draw label is free text the user controls (via the form, or a
    health file imported from another device/source) and is rendered via
    plain JSX interpolation (frontend/src/app/timeline/page.tsx: `{d.label}`)
    — React escapes this by default, and the codebase has no
    dangerouslySetInnerHTML anywhere, so this should be structurally safe.
    This test proves that property holds and guards it against regressing."""
    payload = "<script>window.__xss_fired = true;</script><img src=x onerror=\"window.__xss_fired = true\">"
    doc = {
        "schema_version": "1.0",
        "exported_at": "2025-01-01T00:00:00Z",
        "series": {"draws": [{"draw_date": "2025-01-01", "label": payload,
                               "values": {"LDL_mgdl": 120, "sex": "M"}}]},
    }
    _import(page, base_url, tmp_path, "xss.json", json.dumps(doc).encode())
    # The payload must appear as literal visible text (proves it was escaped,
    # not silently stripped) ...
    expect(page.get_by_text("2025-01-01 — <script>window.__xss_fired = true;</script>", exact=False)).to_be_visible()
    # ... and must never have executed.
    fired = page.evaluate("() => window.__xss_fired === true")
    assert fired is False
    # No actual <script> or <img onerror> element was injected into the DOM
    # (only an escaped text node containing the same characters).
    assert page.locator("img[onerror]").count() == 0
