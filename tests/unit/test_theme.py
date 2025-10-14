"""Unit tests for XGovukFrontendTheme."""

import pytest
from xgovuk_flask_admin.theme import XGovukFrontendTheme


@pytest.mark.unit
class TestXGovukTheme:
    """Test GOV.UK theme configuration."""

    def test_theme_folder(self):
        """Test theme uses correct template folder."""
        theme = XGovukFrontendTheme()
        assert theme.folder == "admin"

    def test_theme_base_template(self):
        """Test theme uses correct base template."""
        theme = XGovukFrontendTheme()
        assert theme.base_template == "admin/base.html"
