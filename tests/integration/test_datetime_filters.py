"""Tests for custom datetime filters with second-level precision support."""

from datetime import datetime, timedelta
import pytest
from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.orm import declarative_base, Session

from xgovuk_flask_admin import (
    DateTimeEqualFilter,
    DateTimeAfterFilter,
    DateTimeBeforeFilter,
)


Base = declarative_base()


class DateTimeTestModel(Base):
    """Test model with datetime column."""

    __tablename__ = "test_model"

    id = Column("id", DateTime, primary_key=True)
    created_at = Column("created_at", DateTime)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite session with test data."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)

    # Create test records with specific timestamps
    base_time = datetime(2024, 1, 15, 10, 30, 45)  # 2024-01-15 10:30:45.000000

    records = [
        DateTimeTestModel(id=base_time, created_at=base_time),  # Exactly at the second
        DateTimeTestModel(
            id=base_time + timedelta(microseconds=100000),
            created_at=base_time + timedelta(microseconds=100000),
        ),  # 0.1 sec later
        DateTimeTestModel(
            id=base_time + timedelta(microseconds=500000),
            created_at=base_time + timedelta(microseconds=500000),
        ),  # 0.5 sec later
        DateTimeTestModel(
            id=base_time + timedelta(microseconds=999999),
            created_at=base_time + timedelta(microseconds=999999),
        ),  # 0.999999 sec later
        DateTimeTestModel(
            id=base_time + timedelta(seconds=1),
            created_at=base_time + timedelta(seconds=1),
        ),  # Exactly 1 sec later
        DateTimeTestModel(
            id=base_time + timedelta(seconds=2),
            created_at=base_time + timedelta(seconds=2),
        ),  # 2 sec later
        DateTimeTestModel(
            id=base_time - timedelta(seconds=1),
            created_at=base_time - timedelta(seconds=1),
        ),  # 1 sec before
    ]

    for record in records:
        session.add(record)
    session.commit()

    yield session
    session.close()
    engine.dispose()


class TestDateTimeEqualFilter:
    """Tests for DateTimeEqualFilter with second-level precision."""

    def test_exact_microsecond_match(self, db_session):
        """Test that filter matches exact datetime with microseconds."""
        column = DateTimeTestModel.created_at
        exact_time = datetime(2024, 1, 15, 10, 30, 45, 100000)  # With microseconds

        filter_instance = DateTimeEqualFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, exact_time)

        results = filtered_query.all()

        # Should match only the exact record
        assert len(results) == 1
        assert results[0].created_at == exact_time

    def test_second_level_precision_matches_all_within_second(self, db_session):
        """Test that second-level precision matches all records within that second."""
        column = DateTimeTestModel.created_at
        second_level_time = datetime(2024, 1, 15, 10, 30, 45)  # No microseconds

        filter_instance = DateTimeEqualFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, second_level_time)

        results = filtered_query.all()

        # Should match all 4 records within that second (0.0, 0.1, 0.5, 0.999999)
        assert len(results) == 4

        # Verify all results are within the target second
        for result in results:
            assert result.created_at >= second_level_time
            assert result.created_at < second_level_time + timedelta(seconds=1)

    def test_second_level_precision_excludes_next_second(self, db_session):
        """Test that second-level precision doesn't match the next second."""
        column = DateTimeTestModel.created_at
        second_level_time = datetime(2024, 1, 15, 10, 30, 45)

        filter_instance = DateTimeEqualFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, second_level_time)

        results = filtered_query.all()

        # Should not include the record at exactly 1 second later
        result_times = [r.created_at for r in results]
        assert datetime(2024, 1, 15, 10, 30, 46) not in result_times

    def test_operation_name(self):
        """Test that filter returns correct operation name."""
        column = DateTimeTestModel.created_at
        filter_instance = DateTimeEqualFilter(column, "Created At")

        assert filter_instance.operation() == "equals"


class TestDateTimeAfterFilter:
    """Tests for DateTimeAfterFilter with second-level precision."""

    def test_exact_microsecond_after(self, db_session):
        """Test that filter with microseconds uses strict greater-than."""
        column = DateTimeTestModel.created_at
        exact_time = datetime(2024, 1, 15, 10, 30, 45, 100000)

        filter_instance = DateTimeAfterFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, exact_time)

        results = filtered_query.all()

        # Should match only records strictly after (0.5, 0.999999, 1 sec, 2 sec)
        assert len(results) == 4
        for result in results:
            assert result.created_at > exact_time

    def test_second_level_precision_after(self, db_session):
        """Test that second-level precision matches records after that whole second."""
        column = DateTimeTestModel.created_at
        second_level_time = datetime(2024, 1, 15, 10, 30, 45)  # No microseconds

        filter_instance = DateTimeAfterFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, second_level_time)

        results = filtered_query.all()

        # Should match only records after the entire second (1 sec, 2 sec later)
        assert len(results) == 2

        # All results should be >= second_level_time + 1 second
        for result in results:
            assert result.created_at >= second_level_time + timedelta(seconds=1)

    def test_second_level_precision_excludes_same_second(self, db_session):
        """Test that second-level precision doesn't include records within the same second."""
        column = DateTimeTestModel.created_at
        second_level_time = datetime(2024, 1, 15, 10, 30, 45)

        filter_instance = DateTimeAfterFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, second_level_time)

        results = filtered_query.all()
        result_times = [r.created_at for r in results]

        # Should not include records within the target second
        assert datetime(2024, 1, 15, 10, 30, 45) not in result_times
        assert datetime(2024, 1, 15, 10, 30, 45, 100000) not in result_times
        assert datetime(2024, 1, 15, 10, 30, 45, 999999) not in result_times

    def test_operation_name(self):
        """Test that filter returns correct operation name."""
        column = DateTimeTestModel.created_at
        filter_instance = DateTimeAfterFilter(column, "Created At")

        assert filter_instance.operation() == "after"


class TestDateTimeBeforeFilter:
    """Tests for DateTimeBeforeFilter with second-level precision."""

    def test_exact_microsecond_before(self, db_session):
        """Test that filter with microseconds uses strict less-than."""
        column = DateTimeTestModel.created_at
        exact_time = datetime(2024, 1, 15, 10, 30, 45, 500000)

        filter_instance = DateTimeBeforeFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, exact_time)

        results = filtered_query.all()

        # Should match records before (1 sec before, exactly at second, 0.1 sec later)
        assert len(results) == 3
        for result in results:
            assert result.created_at < exact_time

    def test_second_level_precision_before(self, db_session):
        """Test that second-level precision matches records before that second."""
        column = DateTimeTestModel.created_at
        second_level_time = datetime(2024, 1, 15, 10, 30, 45)  # No microseconds

        filter_instance = DateTimeBeforeFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, second_level_time)

        results = filtered_query.all()

        # Should match only the record before the target second
        assert len(results) == 1
        assert results[0].created_at < second_level_time

    def test_second_level_precision_excludes_same_second(self, db_session):
        """Test that second-level precision doesn't include the target second."""
        column = DateTimeTestModel.created_at
        second_level_time = datetime(2024, 1, 15, 10, 30, 45)

        filter_instance = DateTimeBeforeFilter(column, "Created At")
        query = db_session.query(DateTimeTestModel)
        filtered_query = filter_instance.apply(query, second_level_time)

        results = filtered_query.all()
        result_times = [r.created_at for r in results]

        # Should not include records at or after the target second
        assert datetime(2024, 1, 15, 10, 30, 45) not in result_times
        assert datetime(2024, 1, 15, 10, 30, 45, 100000) not in result_times

    def test_operation_name(self):
        """Test that filter returns correct operation name."""
        column = DateTimeTestModel.created_at
        filter_instance = DateTimeBeforeFilter(column, "Created At")

        assert filter_instance.operation() == "before"


class TestDateTimeFilterIntegration:
    """Integration tests for datetime filters working together."""

    def test_combining_before_and_after_with_second_precision(self, db_session):
        """Test using both before and after filters with second-level precision."""
        column = DateTimeTestModel.created_at

        # Filter for records between 10:30:45 and 10:30:46 (exclusive on both ends)
        after_time = datetime(2024, 1, 15, 10, 30, 44)  # Second-level
        before_time = datetime(2024, 1, 15, 10, 30, 46)  # Second-level

        after_filter = DateTimeAfterFilter(column, "Created At")
        before_filter = DateTimeBeforeFilter(column, "Created At")

        query = db_session.query(DateTimeTestModel)
        query = after_filter.apply(query, after_time)
        query = before_filter.apply(query, before_time)

        results = query.all()

        # Should match records in the 10:30:45 second (4 records)
        assert len(results) == 4

        for result in results:
            # After 10:30:44 means >= 10:30:45
            assert result.created_at >= datetime(2024, 1, 15, 10, 30, 45)
            # Before 10:30:46 means < 10:30:46
            assert result.created_at < datetime(2024, 1, 15, 10, 30, 46)
