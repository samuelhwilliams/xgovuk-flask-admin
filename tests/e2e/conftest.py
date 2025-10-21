"""Playwright fixtures for e2e tests."""

import pytest
from playwright.sync_api import sync_playwright
import subprocess
import time
import requests
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask server in separate process for e2e tests.

    Uses subprocess instead of pytest-flask's live_server to avoid
    async event loop conflicts with Playwright during teardown.

    Note: Does not depend on app/db/admin_instance fixtures to avoid
    Flask context teardown issues.
    """
    import socket

    # Get a free port by binding to port 0 then closing the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    # Create a simple runner script
    runner_code = f"""
import sys
sys.path.insert(0, '{sys.path[0]}')
from example.app import _create_app

app, db, admin = _create_app(config_overrides={{
    'TESTING': True,
    'SQLALCHEMY_ENGINES': {{'default': 'sqlite:///:memory:'}},
}})
app.run(host='127.0.0.1', port={port}, debug=False, use_reloader=False)
"""

    # Start server in subprocess
    # Use DEVNULL to prevent PIPE buffer deadlock after many requests
    server_process = subprocess.Popen(
        [sys.executable, "-c", runner_code],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to be ready
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):  # Try for 5 seconds
        try:
            requests.get(f"{base_url}/admin/", timeout=1)
            break
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.1)
    else:
        server_process.kill()
        raise RuntimeError("Flask server failed to start within 5 seconds")

    yield base_url

    # Cleanup
    server_process.terminate()
    try:
        server_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_process.kill()


@pytest.fixture(scope="session")
def playwright_instance():
    """Create Playwright instance for session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Override browser launch args to add custom options."""
    return {
        **browser_type_launch_args,
        "args": ["--disable-dev-shm-usage"],  # Helps with Docker/CI environments
    }


@pytest.fixture(scope="session")
def browser(playwright_instance, browser_type_launch_args):
    """Create browser instance for session using pytest-playwright options."""
    browser = playwright_instance.chromium.launch(**browser_type_launch_args)
    yield browser
    browser.close()


@pytest.fixture
def context(browser):
    """Create new browser context for each test."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-GB",
    )
    yield context
    context.close()


@pytest.fixture
def page(context, flask_server):
    """Create new page for each test with base URL configured."""
    page = context.new_page()
    page.base_url = flask_server
    page.set_default_timeout(2500)  # Set default timeout to 5 seconds
    yield page
    page.close()


@pytest.fixture
def mobile_page(browser, flask_server):
    """Create page with mobile viewport."""
    context = browser.new_context(
        viewport={"width": 375, "height": 667},  # iPhone SE size
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
    )
    page = context.new_page()
    page.base_url = flask_server
    page.set_default_timeout(2500)  # Set default timeout to 5 seconds
    yield page
    context.close()


@pytest.fixture
def tablet_page(browser, flask_server):
    """Create page with tablet viewport."""
    context = browser.new_context(
        viewport={"width": 768, "height": 1024},  # iPad size
    )
    page = context.new_page()
    page.base_url = flask_server
    page.set_default_timeout(2500)  # Set default timeout to 5 seconds
    yield page
    context.close()


# Screenshot directory for visual regression testing
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


@pytest.fixture
def screenshot(request):
    """Fixture to capture screenshots for visual regression testing.

    Screenshots are only captured when CI or VISUAL_TESTS environment variables are set.
    This allows tests to call screenshot() unconditionally without slowing down local runs.

    Usage in tests:
        def test_my_feature(page, screenshot):
            page.goto("/some/url")
            screenshot(page, "my-feature-name")  # Creates my-feature-name-desktop.png

        def test_mobile_feature(mobile_page, screenshot):
            mobile_page.goto("/some/url")
            screenshot(mobile_page, "my-feature-name")  # Creates my-feature-name-mobile.png
    """
    import os

    def _screenshot(page_obj, name: str, full_page: bool = True):
        """Capture a screenshot for visual regression testing.

        Args:
            page_obj: Playwright page object (page, mobile_page, or tablet_page)
            name: Base name for the screenshot (without extension)
            full_page: Whether to capture the full scrollable page (default: True)
        """
        # Only capture screenshots in CI or when explicitly enabled
        if not (os.getenv("CI") or os.getenv("VISUAL_TESTS")):
            return

        # Detect viewport size from page to determine suffix
        viewport = page_obj.viewport_size
        if viewport["width"] == 375:
            suffix = "mobile"
        elif viewport["width"] == 768:
            suffix = "tablet"
        else:
            suffix = "desktop"

        filename = f"{name}-{suffix}.png"
        screenshot_path = SCREENSHOT_DIR / filename
        page_obj.screenshot(path=str(screenshot_path), full_page=full_page)

    return _screenshot
