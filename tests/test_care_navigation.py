"""
tests/test_care_navigation.py

Tests for the care-navigation prompts (family/cascade screening + culturally-
tailored prevention support). These are informational next-steps, never clinical
advice — so they must avoid diagnostic/prescriptive/predictive language.
"""
from __future__ import annotations

import re

from fastapi.testclient import TestClient

from api.main import app
from sahc_risklens.clinical.care_navigation import get_care_navigation

client = TestClient(app)


def test_none_for_non_south_asian_without_high_lpa():
    assert get_care_navigation({"LDL_mgdl": 100}) == []
    assert get_care_navigation({"south_asian": False, "Lpa_mgdl": 20}) == []


def test_south_asian_gets_both_prompts():
    items = get_care_navigation({"south_asian": True})
    titles = {i["title"] for i in items}
    assert "Family & screening" in titles
    assert "Culturally-tailored prevention" in titles


def test_high_lpa_triggers_family_screening_even_if_not_south_asian():
    items = get_care_navigation({"south_asian": False, "Lpa_mgdl": 70})
    titles = {i["title"] for i in items}
    assert "Family & screening" in titles
    # No culturally-tailored item without South Asian ancestry.
    assert "Culturally-tailored prevention" not in titles
    # Family text references inherited Lp(a) / cascade screening.
    fam = next(i for i in items if i["title"] == "Family & screening")
    assert "cascade" in fam["description"].lower()


def test_language_is_non_prescriptive_non_diagnostic():
    items = get_care_navigation({"south_asian": True, "Lpa_mgdl": 70})
    blob = " ".join(i["description"] for i in items).lower()
    banned = [r"you have [a-z]", r"you are high risk", r"this predicts", r"you should take"]
    for pat in banned:
        assert not re.search(pat, blob), pat


def test_api_includes_care_navigation():
    body = client.post("/api/v1/benchmark", json={"south_asian": True, "Lpa_mgdl": 60}).json()
    assert any(i["title"] == "Family & screening" for i in body["care_navigation"])


def test_api_empty_when_not_applicable():
    body = client.post("/api/v1/benchmark", json={"LDL_mgdl": 100}).json()
    assert body["care_navigation"] == []
