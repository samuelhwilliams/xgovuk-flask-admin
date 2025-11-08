"""Playwright fixtures for e2e tests."""

import os
import pytest
from playwright.sync_api import sync_playwright
import subprocess
import tempfile
import time
import requests
import sys


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
from testcontainers.postgres import PostgresContainer

# Start PostgreSQL container
postgres = PostgresContainer("postgres:16-alpine")
postgres.start()

app, db, admin = _create_app(config_overrides={{
    'TESTING': True,
    'SQLALCHEMY_ENGINES': {{'default': postgres.get_connection_url().replace('+psycopg2', '')}},
}})
app.run(host='127.0.0.1', port={port}, debug=False, use_reloader=False)
"""

    # Start server in subprocess
    # In CI environments (GitHub Actions, etc.), Docker/testcontainers can be slower,
    # so we need to capture stderr to diagnose issues and use a longer timeout
    is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
    
    # Create temporary files for stdout/stderr to diagnose startup issues
    stderr_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log')
    stdout_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log')
    
    try:
        server_process = subprocess.Popen(
            [sys.executable, "-c", runner_code],
            stdout=stdout_file,
            stderr=stderr_file,
        )

        # Wait for server to be ready
        # Use longer timeout in CI (60 seconds) vs local (10 seconds)
        max_attempts = 600 if is_ci else 100
        base_url = f"http://127.0.0.1:{port}"
        
        for _ in range(max_attempts):
            try:
                requests.get(f"{base_url}/admin/", timeout=1)
                break
            except (requests.ConnectionError, requests.Timeout):
                time.sleep(0.1)
        else:
            # Server failed to start - read error output
            server_process.kill()
            stderr_file.seek(0)
            stdout_file.seek(0)
            stderr_content = stderr_file.read()
            stdout_content = stdout_file.read()
            
            timeout_seconds = max_attempts / 10
            error_msg = f"Flask server failed to start within {timeout_seconds} seconds"
            if stderr_content:
                error_msg += f"\n\nStderr output:\n{stderr_content}"
            if stdout_content:
                error_msg += f"\n\nStdout output:\n{stdout_content}"
            
            raise RuntimeError(error_msg)
    finally:
        # Close the temp files
        stderr_file.close()
        stdout_file.close()

    yield base_url

    # Cleanup
    server_process.terminate()
    try:
        server_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_process.kill()
    
    # Clean up temporary files
    try:
        os.unlink(stderr_file.name)
        os.unlink(stdout_file.name)
    except:
        pass  # Best effort cleanup


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
