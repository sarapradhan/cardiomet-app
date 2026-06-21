"""
Shared fixtures for the browser test suite.

Builds the frontend static export, starts the single-container app (FastAPI
serving both the UI and the API), and yields a live base URL. Skips cleanly if
the build toolchain or Playwright/Chromium is unavailable, so the suite never
blocks a backend-only environment.
"""
from __future__ import annotations

import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
OUT = FRONTEND / "out"

playwright = pytest.importorskip("playwright.sync_api", reason="playwright not installed")
from playwright.sync_api import sync_playwright  # noqa: E402


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait(url: str, timeout: float = 30) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


@pytest.fixture(scope="session")
def base_url():
    # Ensure a static export exists (build once if missing).
    if not (OUT / "index.html").exists():
        if not (FRONTEND / "node_modules").exists():
            pytest.skip("frontend deps not installed; run npm install in frontend/")
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND,
                       env={**os.environ, "NEXT_PUBLIC_API_URL": ""}, check=True)

    port = _free_port()
    proc = subprocess.Popen(
        ["python3", "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        if not _wait(f"{url}/health"):
            proc.terminate()
            pytest.skip("single-container app did not become healthy")
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser, base_url):
    ctx = browser.new_context(viewport={"width": 1100, "height": 1400})
    pg = ctx.new_page()
    # Start each test with clean storage so state never leaks between tests.
    pg.goto(f"{base_url}/", wait_until="domcontentloaded")
    pg.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
    yield pg
    ctx.close()
