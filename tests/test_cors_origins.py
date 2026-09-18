"""
CORS origin policy.

A preview deployment gets a freshly generated hostname on every build, so an
exact-match allowlist can never cover it. When the origin is not allowed, the
browser's preflight is rejected and the UI shows a bare "Failed to fetch" on its
primary action — the page renders fine and the app is dead, which is a hard
failure mode to read from the outside. These tests pin both halves of the
policy: the exact list still works, the regex covers generated hostnames, and
neither one quietly allows everything.
"""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

PREFLIGHT = {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
}


def _client(monkeypatch, **env):
    for key in ("ALLOWED_ORIGINS", "ALLOWED_ORIGIN_REGEX"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import api.main
    return TestClient(importlib.reload(api.main).app)


def _preflight(client, origin):
    return client.options(
        "/api/v1/benchmark", headers={"Origin": origin, **PREFLIGHT})


def test_exact_allowlist_permits_its_own_origin(monkeypatch):
    client = _client(monkeypatch, ALLOWED_ORIGINS="https://cardiometlens.vercel.app")
    r = _preflight(client, "https://cardiometlens.vercel.app")
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "https://cardiometlens.vercel.app"


def test_unlisted_origin_is_refused(monkeypatch):
    client = _client(monkeypatch, ALLOWED_ORIGINS="https://cardiometlens.vercel.app")
    r = _preflight(client, "https://not-ours.example.com")
    assert "access-control-allow-origin" not in r.headers


def test_regex_covers_generated_preview_hostnames(monkeypatch):
    """The case the exact list structurally cannot handle."""
    client = _client(
        monkeypatch,
        ALLOWED_ORIGINS="https://cardiometlens.vercel.app",
        ALLOWED_ORIGIN_REGEX=r"^https://[a-z0-9-]+-saras-projects-81420e9f\.vercel\.app$",
    )
    for origin in (
        "https://website-4h5zds645-saras-projects-81420e9f.vercel.app",
        "https://cardiometlens-demo-orpjzizqt-saras-projects-81420e9f.vercel.app",
    ):
        r = _preflight(client, origin)
        assert r.headers.get("access-control-allow-origin") == origin, origin


@pytest.mark.parametrize("origin", [
    "https://evil.example.com",
    "https://saras-projects-81420e9f.vercel.app.evil.com",
    "http://website-abc-saras-projects-81420e9f.vercel.app",   # http, not https
])
def test_regex_stays_anchored(monkeypatch, origin):
    """An unanchored or sloppy regex would hand CORS to anyone."""
    client = _client(
        monkeypatch,
        ALLOWED_ORIGINS="https://cardiometlens.vercel.app",
        ALLOWED_ORIGIN_REGEX=r"^https://[a-z0-9-]+-saras-projects-81420e9f\.vercel\.app$",
    )
    r = _preflight(client, origin)
    assert "access-control-allow-origin" not in r.headers, origin


def test_default_is_local_dev_only(monkeypatch):
    """Configuring neither var must not fall open."""
    client = _client(monkeypatch)
    assert _preflight(client, "http://localhost:3000").status_code == 200
    assert "access-control-allow-origin" not in _preflight(
        client, "https://cardiometlens.vercel.app").headers
