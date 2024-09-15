"""Unit tests for XGovFrontendTheme."""

import pytest
from xgov_flask_admin import XGovFrontendTheme


@pytest.mark.unit
class TestXGovTheme:
    """Test GOV.UK theme configuration."""

    def test_theme_folder(self):
        """Test theme uses correct template folder."""
        theme = XGovFrontendTheme()
        assert theme.folder == "admin"

    def test_theme_base_template(self):
        """Test theme uses correct base template."""
        theme = XGovFrontendTheme()
        assert theme.base_template == "admin/base.html"
