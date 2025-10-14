"""Custom WTForms widgets for xgovuk-flask-admin."""

from govuk_frontend_wtf.gov_form_base import GovFormBase
from govuk_frontend_wtf.wtforms_widgets import GovDateInput as _GovDateInput
from wtforms.widgets.core import Select


class GovDateInput(_GovDateInput):
    """Extended GovDateInput that properly merges fieldset params instead of using setdefault.

    This allows widget_args to customize the fieldset legend classes (e.g., for bold styling).
    """

    def map_gov_params(self, field, **kwargs):
        params = super().map_gov_params(field, **kwargs)

        # The parent uses setdefault which won't merge with existing fieldset params.
        # We need to ensure the legend text is set if not already present,
        # while preserving any classes or other params passed in widget_args.
        # NOTE: this feels like a bug in govuk-frontend-wtf
        if "fieldset" not in params:
            params["fieldset"] = {}
        if "legend" not in params["fieldset"]:
            params["fieldset"]["legend"] = {}
        if "text" not in params["fieldset"]["legend"]:
            params["fieldset"]["legend"]["text"] = field.label.text

        return params


class GovSelectWithSearch(GovFormBase, Select):
    """
    GOV.UK Select widget enhanced with search functionality using Choices.js.

    Based on the select-with-search component from govuk_publishing_components:
    https://github.com/alphagov/govuk_publishing_components/tree/main/app/views/govuk_publishing_components/components/select_with_search

    Uses Choices.js for progressive enhancement:
    https://github.com/Choices-js/Choices

    Renders a <select> element with data-module="select-with-search"
    which is progressively enhanced by Choices.js for search and multi-select.

    This widget supports both single-select and multi-select modes.
    Unlike the standard GovSelect, this widget allows multiple selection
    which is acceptable when combined with search functionality.

    The Python widget is custom implementation for Flask-Admin/WTForms,
    while the JavaScript/CSS are adapted from govuk_publishing_components.
    """

    template = "select-with-search.html"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)

        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True

        kwargs["items"] = []

        # Construct select box choices
        for val, label, selected, render_kw in field.iter_choices():
            item = {"text": label, "value": val, "selected": selected}
            kwargs["items"].append(item)

        # Pass multiple flag to template
        kwargs["multiple"] = self.multiple

        return super().__call__(field, **kwargs)

    def map_gov_params(self, field, **kwargs):
        # Save items list before parent deletes it from kwargs
        select_items = kwargs.get("items", [])
        multiple = kwargs.get("multiple", False)

        params = super().map_gov_params(field, **kwargs)

        # Use 'select_items' to avoid collision with dict.items() method
        params["select_items"] = select_items
        params["multiple"] = multiple

        return params


class GovDateTimeInput(GovFormBase):
    """Renders six input fields representing Day, Month, Year, Hour, Minute, and Second.

    To be used as a widget for WTForms' DateTimeField.
    The input field labels are hardcoded to match GOV.UK Design System patterns.
    The provided label is set as a legend above the input fields.
    The field names MUST all be the same for this widget to work.
    """

    template = "datetime-input.html"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return super().__call__(field, **kwargs)

    def map_gov_params(self, field, **kwargs):
        params = super().map_gov_params(field, **kwargs)
        day, month, year, hour, minute, second = [None] * 6
        if field.raw_data is not None:
            # raw_data comes from form submission as 6 separate values
            day, month, year, hour, minute, second = field.raw_data
        elif field.data:
            # field.data is a datetime object when rendering existing data
            day, month, year = field.data.strftime("%d %m %Y").split(" ")
            hour, minute, second = field.data.strftime("%H %M %S").split(" ")

        # Set up fieldset with legend, merging with any existing params
        if "fieldset" not in params:
            params["fieldset"] = {}
        if "legend" not in params["fieldset"]:
            params["fieldset"]["legend"] = {}
        # Set text if not already set
        if "text" not in params["fieldset"]["legend"]:
            params["fieldset"]["legend"]["text"] = field.label.text
        params.setdefault(
            "items",
            [
                {
                    "label": "Day",
                    "id": "{}-day".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": day,
                },
                {
                    "label": "Month",
                    "id": "{}-month".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": month,
                },
                {
                    "label": "Year",
                    "id": "{}-year".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-4",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": year,
                },
                {
                    "label": "Hour",
                    "id": "{}-hour".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": hour,
                },
                {
                    "label": "Minute",
                    "id": "{}-minute".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": minute,
                },
                {
                    "label": "Second",
                    "id": "{}-second".format(field.name),
                    "name": field.name,
                    "classes": " ".join(
                        [
                            "govuk-input--width-2",
                            "govuk-input--error" if field.errors else "",
                        ]
                    ).strip(),
                    "value": second,
                },
            ],
        )
        return params
