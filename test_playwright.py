"""Simple smoke test to verify the Playwright installation works.

Launches headless Chromium, loads a data: URL, and checks the page title.
Run with: python test_playwright.py
"""

from importlib.metadata import version

from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content("<title>Playwright OK</title><h1>Hello from Playwright</h1>")

        title = page.title()
        heading = page.inner_text("h1")
        browser.close()

    assert title == "Playwright OK", f"unexpected title: {title!r}"
    assert heading == "Hello from Playwright", f"unexpected heading: {heading!r}"

    print(f"Playwright version: {version('playwright')}")
    print(f"Page title:        {title}")
    print(f"Page heading:      {heading}")
    print("SUCCESS: Playwright + Chromium are working.")


if __name__ == "__main__":
    main()
