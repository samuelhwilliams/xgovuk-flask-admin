"""Integration tests for export functionality."""

import pytest


@pytest.mark.integration
class TestExport:
    """Test CSV export functionality."""

    @pytest.mark.xfail(reason="Not implemented: Assert export button present")
    def test_export_button_shown(self, client, sample_users):
        """Test export button is displayed when enabled."""
        client.get("/admin/user/")
        # TODO: Assert export button present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Request CSV export and verify all users present"
    )
    def test_csv_export_all_records(self, client, sample_users):
        """Test CSV export includes all records."""
        # TODO: Request CSV export
        # TODO: Parse CSV and verify all users present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Request CSV export with filter and verify only filtered records"
    )
    def test_csv_export_with_filters(self, client, sample_users):
        """Test CSV export respects active filters."""
        # TODO: Request CSV export with filter
        # TODO: Verify only filtered records in CSV
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Request CSV export and verify CSV headers present"
    )
    def test_csv_export_headers(self, client, sample_users):
        """Test CSV export includes column headers."""
        # TODO: Request CSV export
        # TODO: Verify CSV headers present
        raise NotImplementedError("Test not implemented")

    @pytest.mark.xfail(
        reason="Not implemented: Request CSV export and verify content type is text/csv"
    )
    def test_csv_export_content_type(self, client, sample_users):
        """Test CSV export has correct content type."""
        # TODO: Request CSV export
        # TODO: Verify content type is text/csv
        raise NotImplementedError("Test not implemented")
