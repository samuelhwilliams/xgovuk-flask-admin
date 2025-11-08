"""Integration tests for array filter functionality."""

import pytest

from example.models import Account, Tag
from tests.factories import AccountFactory, UserFactory
from xgovuk_flask_admin.filters import (
    ArrayNotContainsFilter,
    ArrayOverlapFilter,
    ArrayEqualFilter,
)


@pytest.fixture
def array_test_data(db_session):
    user = UserFactory()

    accounts = [
        AccountFactory(
            id="1", user_id=user.id, tags=[Tag.RED, Tag.BLUE], notes=["note1", "note2"]
        ),
        AccountFactory(id="2", user_id=user.id, tags=[Tag.YELLOW], notes=["note3"]),
        AccountFactory(
            id="3",
            user_id=user.id,
            tags=[Tag.RED, Tag.YELLOW],
            notes=["note1", "note4"],
        ),
        AccountFactory(id="4", user_id=user.id, tags=[Tag.BLUE], notes=["note5"]),
        AccountFactory(id="5", user_id=user.id, tags=[], notes=[]),
        AccountFactory(id="6", user_id=user.id, tags=[], notes=["note6", "note7"]),
    ]

    db_session.flush()
    return accounts


@pytest.mark.integration
class TestArrayNotContainsFilter:
    def test_enum_array_not_contains(self, db_session, array_test_data):
        column = Account.tags
        filter_instance = ArrayNotContainsFilter(column, "Tags")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, "RED")

        results = filtered_query.all()

        for result in results:
            if result.tags:
                assert Tag.RED not in result.tags

    def test_not_contains_includes_empty_and_null(self, db_session, array_test_data):
        column = Account.tags
        filter_instance = ArrayNotContainsFilter(column, "Tags")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, "RED")

        results = filtered_query.all()

        result_ids = [r.id for r in results]
        assert "5" in result_ids
        assert "6" in result_ids

    def test_operation_name(self):
        column = Account.tags
        filter_instance = ArrayNotContainsFilter(column, "Tags")
        assert filter_instance.operation() == "not contains"


@pytest.mark.integration
class TestArrayOverlapFilter:
    def test_enum_array_overlap_single_value(self, db_session, array_test_data):
        column = Account.tags
        filter_instance = ArrayOverlapFilter(column, "Tags")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, "YELLOW")

        results = filtered_query.all()

        assert len(results) == 2
        assert all(Tag.YELLOW in r.tags for r in results if r.tags)

    def test_enum_array_overlap_multiple_values(self, db_session, array_test_data):
        column = Account.tags
        filter_instance = ArrayOverlapFilter(column, "Tags")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, ["RED", "YELLOW"])

        results = filtered_query.all()

        assert len(results) == 3
        for result in results:
            if result.tags:
                assert Tag.RED in result.tags or Tag.YELLOW in result.tags

    def test_text_array_overlap(self, db_session, array_test_data):
        column = Account.notes
        filter_instance = ArrayOverlapFilter(column, "Notes")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, ["note1", "note5"])

        results = filtered_query.all()

        assert len(results) == 3
        for result in results:
            if result.notes:
                assert "note1" in result.notes or "note5" in result.notes

    def test_operation_name(self):
        column = Account.tags
        filter_instance = ArrayOverlapFilter(column, "Tags")
        assert filter_instance.operation() == "has any of"


@pytest.mark.integration
class TestArrayEqualFilter:
    def test_enum_array_equals_exact_match(self, db_session, array_test_data):
        column = Account.tags
        filter_instance = ArrayEqualFilter(column, "Tags")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, ["RED", "BLUE"])

        results = filtered_query.all()

        assert len(results) == 1
        assert results[0].id == "1"
        assert results[0].tags == [Tag.RED, Tag.BLUE]

    def test_text_array_equals_empty(self, db_session, array_test_data):
        column = Account.notes
        filter_instance = ArrayEqualFilter(column, "Notes")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, [])

        results = filtered_query.all()

        assert len(results) == 1
        assert results[0].id == "5"
        assert results[0].notes == []

    def test_equals_single_value_as_string(self, db_session, array_test_data):
        column = Account.tags
        filter_instance = ArrayEqualFilter(column, "Tags")
        query = db_session.query(Account)
        filtered_query = filter_instance.apply(query, "YELLOW")

        results = filtered_query.all()

        assert len(results) == 1
        assert results[0].id == "2"
        assert results[0].tags == [Tag.YELLOW]

    def test_operation_name(self):
        column = Account.tags
        filter_instance = ArrayEqualFilter(column, "Tags")
        assert filter_instance.operation() == "equals"


@pytest.mark.integration
class TestArrayFilterIntegration:
    def test_combining_overlap_and_not_contains(self, db_session, array_test_data):
        column = Account.tags

        overlap_filter = ArrayOverlapFilter(column, "Tags")
        not_contains_filter = ArrayNotContainsFilter(column, "Tags")

        query = db_session.query(Account)
        query = overlap_filter.apply(query, ["BLUE"])
        query = not_contains_filter.apply(query, "RED")

        results = query.all()

        assert len(results) == 1
        assert results[0].id == "4"
        assert Tag.BLUE in results[0].tags
        assert Tag.RED not in results[0].tags

    def test_overlap_with_multiple_values(self, db_session, array_test_data):
        column = Account.tags

        overlap_filter = ArrayOverlapFilter(column, "Tags")

        query = db_session.query(Account)
        query = overlap_filter.apply(query, ["RED", "BLUE"])

        results = query.all()

        assert len(results) == 3
        for result in results:
            if result.tags:
                assert Tag.RED in result.tags or Tag.BLUE in result.tags
