import inspect
from datetime import datetime
import typing as t

import sqlalchemy
from flask import Flask, send_from_directory, request
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.contrib.sqla.tools import is_relationship
from flask_admin.model.form import converts
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovSelect

from xgovuk_flask_admin.assets import (
    xgovuk_flask_admin_include_css,
    xgovuk_flask_admin_include_js,
    ROOT_DIR,
)
from xgovuk_flask_admin.filters import (
    XGovukFilterConverter,
)
from xgovuk_flask_admin.pagination import govuk_pagination_params_builder
from xgovuk_flask_admin.widgets import (
    GovSelectWithSearch,
    GovDateInput,
    GovDateTimeInput,
)
from sqlalchemy.orm import ColumnProperty
from wtforms import validators, SelectField
from enum import Enum


class XGovukFlaskAdmin:
    def __init__(self, app: Flask, service_name: str | None = None):
        self.service_name = service_name

        if app is not None:
            self.init_app(app)

    def __inject_jinja2_global_variables(self, app):
        @app.context_processor
        def inject_xgovuk_flask_admin_globals():
            return {"xgovuk_flask_admin_service_name": self.service_name}

        app.template_global("xgovuk_flask_admin_include_css")(
            xgovuk_flask_admin_include_css
        )
        app.template_global("xgovuk_flask_admin_include_js")(
            xgovuk_flask_admin_include_js
        )
        app.template_global("govuk_pagination_data_builder")(
            govuk_pagination_params_builder
        )

    def __setup_static_routes(self, app):
        if not app.url_map.host_matching:
            app.route(
                "/_xgovuk_flask_admin/<path:filename>",
                endpoint="xgovuk_flask_admin.static",
            )(self.static)

        else:
            app.route(
                "/_xgovuk_flask_admin/<path:filename>",
                endpoint="xgovuk_flask_admin.static",
                host="<xgovuk_flask_admin_host>",
            )(self.static)

            @app.url_defaults
            def inject_admin_routes_host_if_required(
                endpoint: str, values: t.Dict[str, t.Any]
            ) -> None:
                if app.url_map.is_endpoint_expecting(
                    endpoint, "xgovuk_flask_admin_host"
                ):
                    values.setdefault("xgovuk_flask_admin_host", request.host)

            # Automatically strip `admin_routes_host` from the endpoint values so
            # that the view methods don't receive that parameter, as it's not actually
            # required by any of them.
            @app.url_value_preprocessor
            def strip_admin_routes_host_from_static_endpoint(
                endpoint: t.Optional[str], values: t.Optional[t.Dict[str, t.Any]]
            ) -> None:
                if (
                    endpoint
                    and values
                    and app.url_map.is_endpoint_expecting(
                        endpoint, "xgovuk_flask_admin_host"
                    )
                ):
                    values.pop("xgovuk_flask_admin_host", None)

    def init_app(self, app: Flask, service_name: str | None = None):
        service_name = service_name or self.service_name

        self.__inject_jinja2_global_variables(app)
        self.__setup_static_routes(app)

    def static(self, filename):
        """Serve main CSS/JS assets from static/dist/assets/."""
        dist = str(ROOT_DIR / "static" / "dist" / "assets")
        return send_from_directory(dist, filename, max_age=60 * 60 * 24 * 7 * 52)


class XGovukAdminModelConverter(AdminModelConverter):
    def __init__(self, session, view):
        super().__init__(session, view)

        self.sqlalchemy_type_field_args = {
            "String": {"widget": GovTextInput()},
            "Integer": {"widget": GovTextInput()},
            "Date": {"widget": GovDateInput(), "format": "%d %m %Y"},
            "DateTime": {"widget": GovDateTimeInput(), "format": "%d %m %Y %H %M %S"},
        }

        self.sqlalchemy_type_widget_args = {
            "String": {},
            "Integer": {"params": {"inputmode": "numeric"}},
        }

    def map_column_via_lookup_table(
        self,
        column,
        lookup: t.Literal["sqlalchemy_type_field_args", "sqlalchemy_type_widget_args"],
    ):
        lookup_table = getattr(self, lookup)

        if self.use_mro:
            types = inspect.getmro(type(column.type))
        else:
            types = [type(column.type)]

        # Search by module + name
        for col_type in types:
            type_string = "%s.%s" % (col_type.__module__, col_type.__name__)

            if type_string in lookup_table:
                return lookup_table[type_string]

        # Search by name
        for col_type in types:
            if col_type.__name__ in lookup_table:
                return lookup_table[col_type.__name__]

        return None

    @converts("sqlalchemy.sql.sqltypes.Enum")
    def convert_enum(self, column, field_args, **extra):
        """Convert Enum columns to GOV.UK select fields."""
        # Build choices: value=enum.name (e.g., 'RED'), label=enum.value (e.g., 'red')
        available_choices = [(e.name, e.value) for e in column.type.enum_class]
        accepted_values = [choice[0] for choice in available_choices]

        if column.nullable:
            field_args["allow_blank"] = column.nullable
            accepted_values.append(None)
            # Add blank choice at the beginning
            available_choices.insert(0, ("", ""))

        self._nullable_common(column, field_args)

        field_args["choices"] = available_choices
        field_args["validators"].append(validators.AnyOf(accepted_values))
        field_args["coerce"] = (
            lambda v: v.name if isinstance(v, Enum) else str(v) if v else v
        )
        field_args["widget"] = GovSelect()

        return SelectField(**field_args)

    def _convert_relation(self, name, prop, property_is_association_proxy, kwargs):
        """Override to add GOV.UK Select widget to relationship fields."""
        # Determine if this is a one-to-many or many-to-many relationship (multiple=True)
        # by checking if the relationship has uselist=True
        is_multiple = prop.uselist if hasattr(prop, "uselist") else False

        # Add the appropriate widget to kwargs before field creation
        if is_multiple:
            # Use select-with-search for multi-select (supports search + multiple selection)
            kwargs["widget"] = GovSelectWithSearch(multiple=True)
        else:
            # Use select-with-search for single select (provides accessible autocomplete)
            kwargs["widget"] = GovSelectWithSearch(multiple=False)

        # Call parent to create the field with our widget in kwargs
        return super()._convert_relation(
            name, prop, property_is_association_proxy, kwargs
        )

    # TODO: WIP finish fixing up error messages from wtforms
    # def convert(self, model, mapper, name, prop, field_args, hidden_pk):
    #     field = super().convert(model, mapper, name, prop, field_args, hidden_pk)
    #
    #     if field:
    #         for validator in field.kwargs.get("validators"):
    #             if isinstance(validator, InputRequired):
    #                 validator.message = f"Enter a value for {name.replace('_', ' ')}"
    #
    #     return field


class XGovukModelView(ModelView):
    model_form_converter = XGovukAdminModelConverter
    filter_converter = XGovukFilterConverter()

    # Format enum values to show their .value (lowercase) instead of .name (uppercase)
    # Format datetime values without microseconds for better readability
    column_type_formatters = {
        Enum: lambda view, value, name: value.value
        if isinstance(value, Enum)
        else value,
        datetime: lambda view, value, name: value.strftime("%Y-%m-%d %H:%M:%S")
        if value
        else "",
    }

    def __init__(
        self,
        model,
        session,
        name=None,
        category="Miscellaneous",
        endpoint=None,
        url=None,
        static_folder=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
    ):
        # To simplify the sidebar and ensure the subnav groups well, we force a default category.
        # Suggest overriding this though.
        super().__init__(
            model,
            session,
            name=name,
            category=category,
            endpoint=endpoint,
            url=url,
            static_folder=static_folder,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value,
        )

    def _get_list_filter_args(self):
        """
        Override to combine GOV.UK date input fields before processing filters
        and include filter operation in the result.

        GOV.UK date inputs create three separate fields with -day, -month, -year suffixes.
        Flask-Admin expects a single field with YYYY-MM-DD format. This method intercepts
        the request parameters and combines the GOV.UK date fields before passing them to
        Flask-Admin's filter processing.

        Also enhances the filter data to include the operation name (e.g., "equals", "after")
        for better display in the UI.
        """
        from flask import request, flash
        from werkzeug.datastructures import ImmutableMultiDict

        # Build modified args dict, filtering out empty filter values
        modified = {}
        for key in request.args.keys():
            # Get all values for this key (handles multi-value params)
            values = request.args.getlist(key)

            # Skip empty filter parameters (but keep non-filter params like search, page, etc.)
            # Filter params start with 'flt' followed by digits
            if key.startswith("flt") and all(
                v == "" or (isinstance(v, str) and v.strip() == "") for v in values
            ):
                continue

            if len(values) == 1:
                modified[key] = values[0]
            else:
                modified[key] = values

        # Find and combine GOV.UK date and datetime fields
        # Look for fields ending with -day that start with 'flt'
        for arg in request.args:
            if arg.startswith("flt") and arg.endswith("-day"):
                base = arg[:-4]  # Remove '-day' suffix
                month_key = base + "-month"
                year_key = base + "-year"
                hour_key = base + "-hour"
                minute_key = base + "-minute"
                second_key = base + "-second"

                # Check if this is a datetime field (has time components)
                is_datetime = (
                    hour_key in request.args
                    and minute_key in request.args
                    and second_key in request.args
                )

                if month_key in request.args and year_key in request.args:
                    day = request.args[arg].strip()
                    month = request.args[month_key].strip()
                    year = request.args[year_key].strip()

                    if is_datetime:
                        # DateTime field with 6 components
                        hour = request.args[hour_key].strip()
                        minute = request.args[minute_key].strip()
                        second = request.args[second_key].strip()

                        # Only combine if all six parts are present
                        if day and month and year and hour and minute and second:
                            # Create YYYY-MM-DD HH:MM:SS format
                            modified[base] = (
                                f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
                            )

                            # Remove the individual component fields
                            modified.pop(arg, None)
                            modified.pop(month_key, None)
                            modified.pop(year_key, None)
                            modified.pop(hour_key, None)
                            modified.pop(minute_key, None)
                            modified.pop(second_key, None)
                    else:
                        # Date field with 3 components only
                        if day and month and year:
                            # Create YYYY-MM-DD format, padding day and month to 2 digits
                            modified[base] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

                            # Remove the individual component fields so they don't interfere
                            modified.pop(arg, None)
                            modified.pop(month_key, None)
                            modified.pop(year_key, None)

        # Temporarily replace request.args with modified version for filter processing
        original_args = request.args
        request.args = ImmutableMultiDict(modified)

        try:
            # Process filters manually to include operation name
            if self._filters:
                filters = []

                for arg in request.args:
                    if not arg.startswith("flt"):
                        continue

                    if "_" not in arg:
                        continue

                    pos, key = arg[3:].split("_", 1)

                    if key in self._filter_args:
                        idx, flt = self._filter_args[key]

                        value = request.args[arg]

                        if flt.validate(value):
                            # Get the operation name from the filter
                            operation = flt.operation()
                            # Create tuple with operation: (idx, flt.name, operation, value)
                            from flask_admin.model.helpers import prettify_name

                            data = (
                                pos,
                                (idx, prettify_name(flt.name), operation, value),
                            )
                            filters.append(data)
                        else:
                            flash(self.get_invalid_value_msg(value, flt), "error")

                # Sort filters and return
                return [v[1] for v in sorted(filters, key=lambda n: n[0])]

            return None
        finally:
            # Restore original request.args
            request.args = original_args

    def _get_remove_filter_url(
        self,
        filter_position,
        active_filters,
        return_url,
        sort_column,
        sort_desc,
        search,
        page_size,
        default_page_size,
        extra_args,
    ):
        """
        Generate URL to remove a specific filter while preserving other state.

        :param filter_position: Position of filter to remove in active_filters list
        :param active_filters: List of currently active filters (idx, flt_name, operation, value) tuples
        :param return_url: Base return URL
        :param sort_column: Current sort column index
        :param sort_desc: Whether sort is descending
        :param search: Current search query
        :param page_size: Current page size
        :param default_page_size: Default page size
        :param extra_args: Extra query arguments to preserve
        """
        # Build filter args excluding the one to remove
        # active_filters is a list of (idx, flt_name, operation, value) tuples
        filter_args = {}
        for pos, filter_data in enumerate(active_filters):
            if pos != filter_position:
                # Handle both 3-tuple (old format) and 4-tuple (new format with operation)
                if len(filter_data) == 4:
                    idx, flt_name, operation, value = filter_data
                else:
                    idx, flt_name, value = filter_data

                # Reconstruct filter key using the format Flask-Admin expects
                # The key format is: flt{position}_{arg_name}
                # where arg_name comes from get_filter_arg(idx, filter_obj)
                if idx < len(self._filters):
                    filter_obj = self._filters[idx]
                    arg_name = self.get_filter_arg(idx, filter_obj)
                    filter_key = f"flt{pos}_{arg_name}"
                    filter_args[filter_key] = value

        # Build complete URL with all state preserved
        kwargs = {}

        # Add filters
        kwargs.update(filter_args)

        # Add sort
        if sort_column is not None:
            kwargs["sort"] = sort_column
        if sort_desc:
            kwargs["desc"] = 1

        # Add search
        if search:
            kwargs["search"] = search

        # Add page size if not default
        if page_size and page_size != default_page_size:
            kwargs["page_size"] = page_size

        # Add extra args
        if extra_args:
            kwargs.update(extra_args)

        return self.get_url(".index_view", **kwargs)

    def _get_remove_search_url(
        self,
        filter_args,
        sort_column,
        sort_desc,
        page_size,
        default_page_size,
        extra_args,
    ):
        """
        Generate URL to remove search query while preserving filters and other state.

        :param filter_args: Dictionary of active filter parameters
        :param sort_column: Current sort column index
        :param sort_desc: Whether sort is descending
        :param page_size: Current page size
        :param default_page_size: Default page size
        :param extra_args: Extra query arguments to preserve
        """
        # Build complete URL with all state preserved except search
        kwargs = {}

        # Add all filter arguments
        kwargs.update(filter_args)

        # Add sort
        if sort_column is not None:
            kwargs["sort"] = sort_column
        if sort_desc:
            kwargs["sort_desc"] = 1

        # Add page size if not default
        if page_size and page_size != default_page_size:
            kwargs["page_size"] = page_size

        # Add extra args (excluding search if present)
        if extra_args:
            extra_args_copy = dict(extra_args)
            extra_args_copy.pop("search", None)
            kwargs.update(extra_args_copy)

        return self.get_url(".index_view", **kwargs)

    def _get_filters(self, filters):
        """
        Override to handle 4-tuple filter format (idx, flt_name, operation, value).
        Get active filters as dictionary of URL arguments and values.
        """
        kwargs = {}

        if filters:
            for i, filter_data in enumerate(filters):
                # Handle both 3-tuple (old format) and 4-tuple (new format with operation)
                if len(filter_data) == 4:
                    idx, flt_name, operation, value = filter_data
                else:
                    idx, flt_name, value = filter_data

                key = "flt%d_%s" % (i, self.get_filter_arg(idx, self._filters[idx]))
                kwargs[key] = value

        return kwargs

    def _apply_filters(self, query, count_query, joins, count_joins, filters):
        """
        Override to handle 4-tuple filter format (idx, flt_name, operation, value).
        """
        if not filters:
            return query, count_query, joins, count_joins

        for filter_data in filters:
            # Handle both 3-tuple (old format) and 4-tuple (new format with operation)
            if len(filter_data) == 4:
                idx, _flt_name, _operation, value = filter_data
            else:
                idx, _flt_name, value = filter_data

            # The rest is the same as parent implementation
            # We need to call parent's logic but it expects 3-tuple, so convert back
            original_filter = (idx, _flt_name, value)

            # Apply the filter using the parent's logic by calling it with single filter
            query, count_query, joins, count_joins = super()._apply_filters(
                query, count_query, joins, count_joins, [original_filter]
            )

        return query, count_query, joins, count_joins

    def _iterate_model_fields(self):
        mapper = self.model._sa_class_manager.mapper

        for attr in mapper.attrs:
            if is_relationship(attr) or getattr(attr, "_is_relationship"):
                continue

            column_name = attr.key
            column = getattr(self.model, column_name)
            yield column_name, column

    def _populate_implicit_form_args(self):
        if not self.form_args:
            self.form_args = {}

        # Save original form_args (which may include relationship fields)
        original_form_args = dict(self.form_args)

        converter = self.model_form_converter(self.session, self)

        form_args = {}
        for column_name, column in self._iterate_model_fields():
            form_field_args = (
                converter.map_column_via_lookup_table(
                    column, "sqlalchemy_type_field_args"
                )
                or {}
            )

            form_args[column_name] = form_field_args

        # For each form field, override the default top-level keys with any provided
        # by the subclass.
        for field_name, field_args in form_args.items():
            form_args[field_name] = {**field_args, **original_form_args.get(field_name, {})}

        # Preserve form_args for relationship fields (not processed by _iterate_model_fields)
        for field_name, field_args in original_form_args.items():
            if field_name not in form_args:
                form_args[field_name] = field_args

        self.form_args = form_args

    def _populate_implicit_form_widget_args(self):
        if not self.form_widget_args:
            self.form_widget_args = {}

        converter = self.model_form_converter(self.session, self)

        form_widget_args = {}
        for column_name, column in self._iterate_model_fields():
            widget_args = (
                converter.map_column_via_lookup_table(
                    column, "sqlalchemy_type_widget_args"
                )
                or {}
            )

            # Check if this is a Date or DateTime field (uses fieldset with legend)
            column_type_name = type(column.type).__name__
            uses_fieldset = column_type_name in ("Date", "DateTime")

            if uses_fieldset:
                # For Date/DateTime fields: add bold to fieldset legend
                if "fieldset" not in widget_args:
                    widget_args["fieldset"] = {}
                if "legend" not in widget_args["fieldset"]:
                    widget_args["fieldset"]["legend"] = {}
                if "classes" not in widget_args["fieldset"]["legend"]:
                    widget_args["fieldset"]["legend"]["classes"] = (
                        "govuk-fieldset__legend--s"
                    )
            else:
                # For other fields: add bold to label
                if "label" not in widget_args:
                    widget_args["label"] = {}
                if "classes" not in widget_args["label"]:
                    widget_args["label"]["classes"] = "govuk-label--s"

            form_widget_args[column_name] = widget_args

        # Also process relationship fields to add govuk-label--s class
        for relation in sqlalchemy.inspect(self.model).relationships:
            field_name = relation.key
            # Relationship fields use select widgets, which need label styling
            widget_args = {}
            if "label" not in widget_args:
                widget_args["label"] = {}
            if "classes" not in widget_args["label"]:
                widget_args["label"]["classes"] = "govuk-label--s"
            form_widget_args[field_name] = widget_args

        self.form_widget_args = {**form_widget_args, **self.form_widget_args}

    def scaffold_form(self):
        """
        Create form from the model.
        """
        self._populate_implicit_form_args()
        self._populate_implicit_form_widget_args()

        return super().scaffold_form()
