"""Unit tests for XGovukFilterConverter."""

import pytest
from flask_admin.contrib.sqla import filters as sqla_filters
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base

from xgovuk_flask_admin.filters import (
    XGovukFilterConverter,
    DateAfterFilter,
    DateBeforeFilter,
    DateTimeEqualFilter,
    DateTimeAfterFilter,
    DateTimeBeforeFilter,
)

Base = declarative_base()


class SampleModel(Base):
    """Sample model with various column types for testing."""

    __tablename__ = "sample_model"

    # Non-nullable columns
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    # Nullable columns
    optional_text = Column(String(100), nullable=True)
    optional_number = Column(Integer, nullable=True)


class TestXGovukFilterConverter:
    """Test XGovukFilterConverter customizations."""

    @pytest.fixture
    def converter(self):
        """Create a XGovukFilterConverter instance."""
        return XGovukFilterConverter()

    def test_string_filters_exclude_in_list(self, converter):
        """Test that string columns don't get 'in list' filters."""
        column = SampleModel.name
        filters = converter.conv_string(column, "Name")

        filter_types = [type(f) for f in filters]

        # Should have standard string filters
        assert sqla_filters.FilterLike in filter_types
        assert sqla_filters.FilterNotLike in filter_types
        assert sqla_filters.FilterEqual in filter_types
        assert sqla_filters.FilterNotEqual in filter_types

        # Should NOT have in list filters
        assert sqla_filters.FilterInList not in filter_types
        assert sqla_filters.FilterNotInList not in filter_types

    def test_int_filters_exclude_in_list(self, converter):
        """Test that integer columns don't get 'in list' filters."""
        column = SampleModel.age
        filters = converter.conv_int(column, "Age")

        filter_types = [type(f) for f in filters]

        # Should have standard integer filters
        assert sqla_filters.IntEqualFilter in filter_types
        assert sqla_filters.IntNotEqualFilter in filter_types
        assert sqla_filters.IntGreaterFilter in filter_types
        assert sqla_filters.IntSmallerFilter in filter_types

        # Should NOT have in list filters
        assert sqla_filters.IntInListFilter not in filter_types
        assert sqla_filters.IntNotInListFilter not in filter_types

    def test_non_nullable_column_excludes_empty_filter(self, converter):
        """Test that non-nullable columns don't get FilterEmpty."""
        # Test non-nullable integer column
        column = SampleModel.age
        filters = converter.conv_int(column, "Age")

        filter_types = [type(f) for f in filters]

        # Should NOT have empty filter for non-nullable column
        assert sqla_filters.FilterEmpty not in filter_types

    def test_nullable_column_includes_empty_filter(self, converter):
        """Test that nullable columns DO get FilterEmpty."""
        # Test nullable integer column
        column = SampleModel.optional_number
        filters = converter.conv_int(column, "Optional Number")

        filter_types = [type(f) for f in filters]

        # SHOULD have empty filter for nullable column
        assert sqla_filters.FilterEmpty in filter_types

    def test_non_nullable_string_excludes_empty_filter(self, converter):
        """Test that non-nullable string columns don't get FilterEmpty."""
        column = SampleModel.name
        filters = converter.conv_string(column, "Name")

        filter_types = [type(f) for f in filters]

        # Should NOT have empty filter for non-nullable column
        assert sqla_filters.FilterEmpty not in filter_types

    def test_nullable_string_includes_empty_filter(self, converter):
        """Test that nullable string columns DO get FilterEmpty."""
        column = SampleModel.optional_text
        filters = converter.conv_string(column, "Optional Text")

        filter_types = [type(f) for f in filters]

        # SHOULD have empty filter for nullable column
        assert sqla_filters.FilterEmpty in filter_types

    def test_boolean_filters_never_include_empty(self, converter):
        """Test that boolean columns never get FilterEmpty (even if nullable)."""
        column = SampleModel.active
        filters = converter.conv_bool(column, "Active")

        filter_types = [type(f) for f in filters]

        # Boolean filters should only be Equal and NotEqual
        assert sqla_filters.BooleanEqualFilter in filter_types
        assert sqla_filters.BooleanNotEqualFilter in filter_types

        # Should NOT have empty filter (booleans can't be empty)
        assert sqla_filters.FilterEmpty not in filter_types

    def test_enum_filters_exclude_in_list(self, converter):
        """Test that enum columns don't get 'in list' filters."""
        # Create a mock enum column
        import enum

        class TestEnum(enum.Enum):
            OPTION_A = "a"
            OPTION_B = "b"

        # Create a test column
        from sqlalchemy import Enum as SQLAEnum

        column = Column("test_enum", SQLAEnum(TestEnum), nullable=False)

        filters = converter.conv_enum(column, "Test Enum")

        filter_types = [type(f) for f in filters]

        # Should have standard enum filters
        assert sqla_filters.EnumEqualFilter in filter_types
        assert sqla_filters.EnumFilterNotEqual in filter_types

        # Should NOT have in list filters
        assert sqla_filters.EnumFilterInList not in filter_types
        assert sqla_filters.EnumFilterNotInList not in filter_types

    def test_enum_nullable_includes_empty(self, converter):
        """Test that nullable enum columns get FilterEmpty."""
        import enum

        class TestEnum(enum.Enum):
            OPTION_A = "a"
            OPTION_B = "b"

        from sqlalchemy import Enum as SQLAEnum

        column = Column("test_enum", SQLAEnum(TestEnum), nullable=True)

        filters = converter.conv_enum(column, "Test Enum")

        filter_types = [type(f) for f in filters]

        # SHOULD have empty filter for nullable enum
        assert sqla_filters.EnumFilterEmpty in filter_types

    def test_enum_non_nullable_excludes_empty(self, converter):
        """Test that non-nullable enum columns don't get FilterEmpty."""
        import enum

        class TestEnum(enum.Enum):
            OPTION_A = "a"
            OPTION_B = "b"

        from sqlalchemy import Enum as SQLAEnum

        column = Column("test_enum", SQLAEnum(TestEnum), nullable=False)

        filters = converter.conv_enum(column, "Test Enum")

        filter_types = [type(f) for f in filters]

        # Should NOT have empty filter for non-nullable enum
        assert sqla_filters.EnumFilterEmpty not in filter_types

    def test_float_filters_exclude_in_list(self, converter):
        """Test that float columns don't get 'in list' filters."""
        from sqlalchemy import Float

        column = Column("test_float", Float, nullable=False)

        filters = converter.conv_float(column, "Test Float")

        filter_types = [type(f) for f in filters]

        # Should have standard float filters
        assert sqla_filters.FloatEqualFilter in filter_types
        assert sqla_filters.FloatNotEqualFilter in filter_types
        assert sqla_filters.FloatGreaterFilter in filter_types
        assert sqla_filters.FloatSmallerFilter in filter_types

        # Should NOT have in list filters
        assert sqla_filters.FloatInListFilter not in filter_types
        assert sqla_filters.FloatNotInListFilter not in filter_types

    def test_date_filters_exclude_empty_for_non_nullable(self, converter):
        """Test that non-nullable date columns don't get FilterEmpty."""
        from sqlalchemy import Date

        column = Column("test_date", Date, nullable=False)

        filters = converter.conv_date(column, "Test Date")

        filter_types = [type(f) for f in filters]

        # Should have standard date filters
        assert sqla_filters.DateEqualFilter in filter_types
        assert sqla_filters.DateNotEqualFilter in filter_types
        assert DateAfterFilter in filter_types  # Custom filter with "after" label
        assert DateBeforeFilter in filter_types  # Custom filter with "before" label

        # Should NOT have the original greater/smaller filters
        assert sqla_filters.DateGreaterFilter not in filter_types
        assert sqla_filters.DateSmallerFilter not in filter_types

        # Should NOT have between filters (removed from XGovukFilterConverter)
        assert sqla_filters.DateBetweenFilter not in filter_types
        assert sqla_filters.DateNotBetweenFilter not in filter_types

        # Should NOT have empty filter for non-nullable column
        assert sqla_filters.FilterEmpty not in filter_types

        # Verify custom filter labels
        after_filter = next(f for f in filters if isinstance(f, DateAfterFilter))
        before_filter = next(f for f in filters if isinstance(f, DateBeforeFilter))
        assert after_filter.operation() == "after"
        assert before_filter.operation() == "before"

    def test_datetime_filters_exclude_empty_for_non_nullable(self, converter):
        """Test that non-nullable datetime columns don't get FilterEmpty."""

        column = Column("test_datetime", DateTime, nullable=False)

        filters = converter.conv_datetime(column, "Test DateTime")

        filter_types = [type(f) for f in filters]

        # Should have custom datetime filters
        assert (
            DateTimeEqualFilter in filter_types
        )  # Custom filter with second-level precision
        assert sqla_filters.DateTimeNotEqualFilter in filter_types
        assert DateTimeAfterFilter in filter_types  # Custom filter with "after" label
        assert DateTimeBeforeFilter in filter_types  # Custom filter with "before" label

        # Should NOT have the original filters
        assert sqla_filters.DateTimeGreaterFilter not in filter_types
        assert sqla_filters.DateTimeSmallerFilter not in filter_types

        # Should NOT have between filters (removed from XGovukFilterConverter)
        assert sqla_filters.DateTimeBetweenFilter not in filter_types
        assert sqla_filters.DateTimeNotBetweenFilter not in filter_types

        # Should NOT have empty filter for non-nullable column
        assert sqla_filters.FilterEmpty not in filter_types

        # Verify custom filter labels
        after_filter = next(f for f in filters if isinstance(f, DateTimeAfterFilter))
        before_filter = next(f for f in filters if isinstance(f, DateTimeBeforeFilter))
        assert after_filter.operation() == "after"
        assert before_filter.operation() == "before"

    def test_uuid_filters_exclude_in_list(self, converter):
        """Test that UUID columns don't get 'in list' filters."""
        # Create a UUID column
        from sqlalchemy.dialects.postgresql import UUID

        column = Column("test_uuid", UUID(as_uuid=True), nullable=False)

        filters = converter.conv_uuid(column, "Test UUID")

        filter_types = [type(f) for f in filters]

        # Should have standard UUID filters
        assert sqla_filters.UuidFilterEqual in filter_types
        assert sqla_filters.UuidFilterNotEqual in filter_types

        # Should NOT have in list filters
        assert sqla_filters.UuidFilterInList not in filter_types
        assert sqla_filters.UuidFilterNotInList not in filter_types

        # Should NOT have empty filter for non-nullable UUID
        assert sqla_filters.FilterEmpty not in filter_types
