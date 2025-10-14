from datetime import datetime, timedelta

from flask_admin.contrib.sqla import filters as sqla_filters


class DateAfterFilter(sqla_filters.DateGreaterFilter):
    def operation(self):
        return "after"


class DateBeforeFilter(sqla_filters.DateSmallerFilter):
    def operation(self):
        return "before"


class DateTimeEqualFilter(sqla_filters.DateTimeEqualFilter):
    def operation(self):
        return "equals"

    def apply(self, query, value, alias=None):
        """Apply filter with second-level precision support.

        If the input datetime has no microseconds, treat it as second-level precision
        and match all datetimes within that second (>= value and < value + 1 second).
        """
        column = self.get_column(alias)

        # If value has no microseconds, it's second-level precision
        # Match all records within that second
        if isinstance(value, datetime) and value.microsecond == 0:
            end_of_second = value + timedelta(seconds=1)
            return query.filter(column >= value).filter(column < end_of_second)

        # Otherwise, exact match
        return query.filter(column == value)


class DateTimeAfterFilter(sqla_filters.DateTimeGreaterFilter):
    def operation(self):
        return "after"

    def apply(self, query, value, alias=None):
        """Apply filter with second-level precision support.

        If the input datetime has no microseconds, treat it as the start of that second
        and filter for datetimes after that second (>= input + 1 second).
        """
        column = self.get_column(alias)

        # If value has no microseconds, it's second-level precision
        # We want to find records after this second, so >= value + 1 second
        if isinstance(value, datetime) and value.microsecond == 0:
            value = value + timedelta(seconds=1)
            return query.filter(column >= value)

        return query.filter(column > value)


class DateTimeBeforeFilter(sqla_filters.DateTimeSmallerFilter):
    def operation(self):
        return "before"

    def apply(self, query, value, alias=None):
        """Apply filter with second-level precision support.

        If the input datetime has no microseconds, treat it as the start of that second
        and filter for datetimes before that second (< input).
        """
        column = self.get_column(alias)
        return query.filter(column < value)


class TimeAfterFilter(sqla_filters.TimeGreaterFilter):
    def operation(self):
        return "after"


class TimeBeforeFilter(sqla_filters.TimeSmallerFilter):
    def operation(self):
        return "before"


class XGovukFilterConverter(sqla_filters.FilterConverter):
    """
    Custom filter converter for GOV.UK Flask Admin.

    Customizations:
    - Removes "in list" and "not in list" filters from all column types
    - Automatically excludes FilterEmpty from non-nullable columns
    - Uses "before" and "after" labels for date/time comparison filters
    """

    # Override filter tuples to exclude InList/NotInList filters globally
    strings = (
        sqla_filters.FilterLike,
        sqla_filters.FilterNotLike,
        sqla_filters.FilterEqual,
        sqla_filters.FilterNotEqual,
        sqla_filters.FilterEmpty,
        # Removed: FilterInList, FilterNotInList
    )

    string_key_filters = (
        sqla_filters.FilterEqual,
        sqla_filters.FilterNotEqual,
        sqla_filters.FilterEmpty,
        # Removed: FilterInList, FilterNotInList
    )

    int_filters = (
        sqla_filters.IntEqualFilter,
        sqla_filters.IntNotEqualFilter,
        sqla_filters.IntGreaterFilter,
        sqla_filters.IntSmallerFilter,
        sqla_filters.FilterEmpty,
        # Removed: IntInListFilter, IntNotInListFilter
    )

    float_filters = (
        sqla_filters.FloatEqualFilter,
        sqla_filters.FloatNotEqualFilter,
        sqla_filters.FloatGreaterFilter,
        sqla_filters.FloatSmallerFilter,
        sqla_filters.FilterEmpty,
        # Removed: FloatInListFilter, FloatNotInListFilter
    )

    enum = (
        sqla_filters.EnumEqualFilter,
        sqla_filters.EnumFilterNotEqual,
        sqla_filters.EnumFilterEmpty,
        # Removed: EnumFilterInList, EnumFilterNotInList
    )

    uuid_filters = (
        sqla_filters.UuidFilterEqual,
        sqla_filters.UuidFilterNotEqual,
        sqla_filters.FilterEmpty,
        # Removed: UuidFilterInList, UuidFilterNotInList
    )

    date_filters = (
        sqla_filters.DateEqualFilter,
        sqla_filters.DateNotEqualFilter,
        DateAfterFilter,  # Custom: "after" instead of "greater than"
        DateBeforeFilter,  # Custom: "before" instead of "smaller than"
        sqla_filters.FilterEmpty,
        # Removed: DateBetweenFilter, DateNotBetweenFilter
    )

    datetime_filters = (
        DateTimeEqualFilter,  # Custom: handles second-level precision
        sqla_filters.DateTimeNotEqualFilter,
        DateTimeAfterFilter,  # Custom: "after" instead of "greater than" + second-level precision
        DateTimeBeforeFilter,  # Custom: "before" instead of "smaller than" + second-level precision
        sqla_filters.FilterEmpty,
        # Removed: DateTimeBetweenFilter, DateTimeNotBetweenFilter
    )

    time_filters = (
        sqla_filters.TimeEqualFilter,
        sqla_filters.TimeNotEqualFilter,
        TimeAfterFilter,  # Custom: "after" instead of "greater than"
        TimeBeforeFilter,  # Custom: "before" instead of "smaller than"
        sqla_filters.FilterEmpty,
        # Removed: TimeBetweenFilter, TimeNotBetweenFilter
    )

    def _get_filter_list(self, column, filter_classes):
        """
        Helper to create filter instances, excluding FilterEmpty for non-nullable columns.

        :param column: SQLAlchemy column
        :param filter_classes: Tuple of filter classes to instantiate
        :return: List of filter instances
        """
        filters = []
        for filter_class in filter_classes:
            # Skip FilterEmpty for non-nullable columns
            if filter_class == sqla_filters.FilterEmpty or issubclass(
                filter_class, sqla_filters.FilterEmpty
            ):
                # Check if column is nullable
                if hasattr(column, "nullable") and not column.nullable:
                    continue  # Skip this filter for non-nullable columns

            filters.append(filter_class)

        return filters

    @sqla_filters.filters.convert(
        "string",
        "char",
        "unicode",
        "varchar",
        "tinytext",
        "text",
        "mediumtext",
        "longtext",
        "unicodetext",
        "nchar",
        "nvarchar",
        "ntext",
        "citext",
        "emailtype",
        "URLType",
        "IPAddressType",
    )
    def conv_string(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.strings)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert(
        "UUIDType", "ColorType", "TimezoneType", "CurrencyType"
    )
    def conv_string_keys(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.string_key_filters)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert("boolean", "tinyint")
    def conv_bool(self, column, name, **kwargs):
        # Boolean columns can't really be "empty" so always exclude FilterEmpty
        return [f(column, name, **kwargs) for f in self.bool_filters]

    @sqla_filters.filters.convert(
        "int",
        "integer",
        "smallinteger",
        "smallint",
        "biginteger",
        "bigint",
        "mediumint",
    )
    def conv_int(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.int_filters)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert(
        "float", "real", "decimal", "numeric", "double_precision", "double"
    )
    def conv_float(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.float_filters)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert("date")
    def conv_date(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.date_filters)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert("datetime", "datetime2", "timestamp", "smalldatetime")
    def conv_datetime(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.datetime_filters)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert("time")
    def conv_time(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.time_filters)
        return [f(column, name, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert("enum")
    def conv_enum(self, column, name, options=None, **kwargs):
        # Preserve the parent's options handling for enums
        if not options:
            options = [(v, v) for v in column.type.enums]

        filter_classes = self._get_filter_list(column, self.enum)
        return [f(column, name, options, **kwargs) for f in filter_classes]

    @sqla_filters.filters.convert("uuid")
    def conv_uuid(self, column, name, **kwargs):
        filter_classes = self._get_filter_list(column, self.uuid_filters)
        return [f(column, name, **kwargs) for f in filter_classes]
