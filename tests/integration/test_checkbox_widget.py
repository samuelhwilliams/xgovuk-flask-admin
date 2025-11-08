"""Integration tests for XGovCheckboxInput widget HTML rendering."""

import pytest
from bs4 import BeautifulSoup


@pytest.mark.integration
class TestXGovCheckboxInputHTML:
    """Test HTML rendering of XGovCheckboxInput widget."""

    def test_checkbox_widget_without_description_no_none_in_html(
        self, client, user_model_view
    ):
        """Test that checkbox HTML does not contain 'None' when no description is provided."""
        response = client.get("/admin/user/new/")
        assert response.status_code == 200

        html = response.data.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # Find the active checkbox (Boolean field)
        active_checkbox = soup.find("input", {"name": "active", "type": "checkbox"})
        assert active_checkbox is not None, "Active checkbox should be present"

        # Find the form group containing the checkbox
        form_group = active_checkbox.find_parent("div", class_="govuk-form-group")
        assert form_group is not None, "Checkbox should be in a govuk-form-group"

        # Get all text within the form group
        form_group_text = form_group.get_text()

        # Should not contain the string "None"
        assert "None" not in form_group_text, (
            "Checkbox form group should not contain 'None' text"
        )

        # Should not have a hint element when description is None
        hint = form_group.find(class_="govuk-hint")
        assert hint is None, (
            "Checkbox should not have a hint element when description is None"
        )

    def test_checkbox_widget_has_govuk_styling(self, client, user_model_view):
        """Test that checkbox widget has proper GOV.UK Design System classes."""
        response = client.get("/admin/user/new/")
        assert response.status_code == 200

        html = response.data.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # Find the active checkbox
        active_checkbox = soup.find("input", {"name": "active", "type": "checkbox"})
        assert active_checkbox is not None

        # Check the checkbox has the correct GOV.UK classes
        checkbox_classes = active_checkbox.get("class", [])
        assert "govuk-checkboxes__input" in checkbox_classes, (
            f"Checkbox should have govuk-checkboxes__input class, got: {checkbox_classes}"
        )

        # Check for the label
        label = soup.find("label", {"for": "active"})
        assert label is not None, "Checkbox should have a label"

        label_classes = label.get("class", [])
        assert "govuk-checkboxes__label" in label_classes, (
            f"Label should have govuk-checkboxes__label class, got: {label_classes}"
        )

        # Check for the checkboxes container
        checkboxes_container = active_checkbox.find_parent(class_="govuk-checkboxes")
        assert checkboxes_container is not None, (
            "Checkbox should be within a govuk-checkboxes container"
        )

    def test_checkbox_renders_correctly_in_form(self, client, user_model_view):
        """Test that the checkbox field is properly integrated into the form."""
        response = client.get("/admin/user/new/")
        assert response.status_code == 200

        html = response.data.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # Find the active checkbox
        active_checkbox = soup.find("input", {"name": "active", "type": "checkbox"})
        assert active_checkbox is not None

        # Verify the checkbox has an id attribute
        checkbox_id = active_checkbox.get("id")
        assert checkbox_id == "active", (
            f"Checkbox should have id='active', got: {checkbox_id}"
        )

        # Verify the label is correctly associated with the checkbox
        label = soup.find("label", {"for": "active"})
        assert label is not None, (
            "Label should be associated with checkbox via 'for' attribute"
        )

        # Verify the label text
        label_text = label.get_text(strip=True)
        assert "Active" in label_text, (
            f"Label should contain 'Active', got: {label_text}"
        )
