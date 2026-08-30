"""
tests/test_cohort_registry.py

Guards the cohort registry and the labeling invariants that survive it.

Replaces tests/test_sahc_cohort.py, which tested a second cohort ("sahc") that
was removed on 2026-08-30 because its provenance could not be established (see
docs/SAHC_COHORT.md). The tests that were about the *cohort* are gone with it;
the tests that were about the *architecture* — honest labels, no cross-labeling,
unknown ids failing loudly — are kept here, plus explicit guards against the
removed cohort or its data creeping back in.
"""
from __future__ import annotations

import typing
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models.results import CohortLabel
from sahc_risklens.benchmark.percentile import (
    SUPPORTED_COHORTS,
    get_benchmark_data,
    get_cohort_percentiles,
)
from sahc_risklens.config import (
    COHORT_LABELS,
    COHORT_NHANES,
    DEFAULT_COHORT,
    NHANES_COHORT_LABEL,
    cohort_label,
)

client = TestClient(app)
PANEL = {"LDL_mgdl": 130, "HDL_mgdl": 45, "age_yr": 55, "sex": "F"}
REPO = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Registry shape
# ---------------------------------------------------------------------------

def test_exactly_the_registered_cohorts_are_supported():
    assert set(SUPPORTED_COHORTS) == set(COHORT_LABELS)
    assert DEFAULT_COHORT in SUPPORTED_COHORTS


def test_api_literal_matches_config_labels():
    """The response-model Literal and config must not drift apart."""
    assert set(typing.get_args(CohortLabel)) == set(COHORT_LABELS.values())


def test_every_cohort_produces_a_benchmark():
    for c in SUPPORTED_COHORTS:
        table = get_cohort_percentiles(c)
        assert table, f"cohort {c} produced no percentiles"
        assert all(p["cohort_label"] == cohort_label(c)
                   for p in get_benchmark_data(PANEL, cohort=c))


def test_unknown_cohort_raises():
    with pytest.raises(ValueError):
        get_cohort_percentiles("not_a_cohort")


def test_api_rejects_unknown_cohort():
    r = client.post("/api/v1/benchmark?cohort=not_a_cohort", json=PANEL)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Labeling invariants (these outlive any individual cohort)
# ---------------------------------------------------------------------------

def test_nhanes_is_never_labeled_south_asian():
    """The intellectual core: a proxy population is never presented as the real
    one. NHANES has no South Asian sample, so its label must not imply one."""
    label = cohort_label(COHORT_NHANES)
    assert label == NHANES_COHORT_LABEL
    assert "south asian" not in label.lower()
    for p in get_benchmark_data(PANEL, cohort=COHORT_NHANES):
        assert "south asian" not in p["cohort_label"].lower()


def test_no_cohort_label_claims_an_institutional_origin():
    """Guards the 2026-08-30 correction: a cohort label names a population, never
    an institution. Registering a cohort attributed to a named clinic or health
    system requires written provenance first (docs/SAHC_COHORT.md)."""
    for label in COHORT_LABELS.values():
        lowered = label.lower()
        for banned in ("heart center", "el camino", "clinical cohort", "clinic"):
            assert banned not in lowered, f"{label!r} claims an institutional origin"


# ---------------------------------------------------------------------------
# Removal guards
# ---------------------------------------------------------------------------

def test_removed_cohort_is_not_registered():
    assert "sahc" not in SUPPORTED_COHORTS
    assert "sahc" not in COHORT_LABELS


def test_api_rejects_the_removed_cohort_rather_than_erroring():
    r = client.post("/api/v1/benchmark?cohort=sahc", json=PANEL)
    assert r.status_code == 422
    assert "sahc" in r.json()["detail"]


def test_unsourced_cohort_data_files_are_gone():
    """The aggregates derived from the unverified source must not return."""
    for rel in (
        "sahc_risklens/data/sahc_demo_cohort.py",
        "sahc_risklens/data/sahc_cohort_loader.py",
        "sahc_risklens/data/strata_tables.json",
        "scripts/build_strata_tables.py",
    ):
        assert not (REPO / rel).exists(), f"{rel} was reintroduced without provenance"
