"""Unit tests for SelectWithSearchFilterInList and SelectWithSearchFilterNotInList."""

from unittest.mock import MagicMock

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from xgovuk_flask_admin.filters import (
    SelectWithSearchFilterInList,
    SelectWithSearchFilterNotInList,
)

Base = declarative_base()


class SampleModel(Base):
    __tablename__ = "swsf_sample"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)


class TestSelectWithSearchFilterInList:
    def _make(self, **overrides):
        defaults = {
            "column": SampleModel.name,
            "name": "Name",
            "options": [("a", "A"), ("b", "B")],
        }
        defaults.update(overrides)
        return SelectWithSearchFilterInList(**defaults)

    def test_data_type_marks_select_with_search(self):
        flt = self._make()
        assert flt.data_type == "select-with-search"

    def test_default_operation_is_in_list(self):
        flt = self._make()
        assert flt.operation() == "in list"

    def test_get_options_with_static_list(self):
        flt = self._make(options=[("x", "X"), ("y", "Y")])
        assert flt.get_options(view=None) == [("x", "X"), ("y", "Y")]

    def test_get_options_invokes_callable_each_call(self):
        counter = {"n": 0}

        def builder():
            counter["n"] += 1
            return [(f"v{counter['n']}", "label")]

        flt = self._make(options=builder)
        assert flt.get_options(view=None) == [("v1", "label")]
        assert flt.get_options(view=None) == [("v2", "label")]
        assert counter["n"] == 2

    def test_clean_splits_comma_separated_string(self):
        flt = self._make()
        assert flt.clean("a,b,c") == ["a", "b", "c"]

    def test_clean_strips_empty_entries(self):
        flt = self._make()
        assert flt.clean("a, ,b,") == ["a", "b"]

    def test_apply_uses_in_predicate(self):
        flt = self._make()
        query = MagicMock()
        flt.apply(query, ["alice", "bob"])
        query.filter.assert_called_once()

    def test_multiple_flag_stored(self):
        assert self._make(multiple=True).multiple is True
        assert self._make(multiple=False).multiple is False

    def test_string_column_path_stored_until_resolved(self):
        flt = SelectWithSearchFilterInList(
            "collection.grant.name",
            "Grant",
            options=[("a", "A")],
        )
        assert flt.column == "collection.grant.name"
        assert flt.name == "Grant"


class TestSelectWithSearchFilterNotInList:
    def _make(self, **overrides):
        defaults = {
            "column": SampleModel.name,
            "name": "Name",
            "options": [("a", "A"), ("b", "B")],
        }
        defaults.update(overrides)
        return SelectWithSearchFilterNotInList(**defaults)

    def test_data_type_marks_select_with_search(self):
        flt = self._make()
        assert flt.data_type == "select-with-search"

    def test_default_operation_is_not_in_list(self):
        flt = self._make()
        assert flt.operation() == "not in list"

    def test_get_options_with_static_list(self):
        flt = self._make(options=[("x", "X"), ("y", "Y")])
        assert flt.get_options(view=None) == [("x", "X"), ("y", "Y")]

    def test_get_options_invokes_callable_each_call(self):
        counter = {"n": 0}

        def builder():
            counter["n"] += 1
            return [(f"v{counter['n']}", "label")]

        flt = self._make(options=builder)
        assert flt.get_options(view=None) == [("v1", "label")]
        assert flt.get_options(view=None) == [("v2", "label")]
        assert counter["n"] == 2

    def test_clean_splits_comma_separated_string(self):
        flt = self._make()
        assert flt.clean("a,b,c") == ["a", "b", "c"]

    def test_apply_uses_not_in_predicate(self):
        flt = self._make()
        query = MagicMock()
        flt.apply(query, ["alice"])
        query.filter.assert_called_once()

    def test_multiple_flag_stored(self):
        assert self._make(multiple=True).multiple is True
        assert self._make(multiple=False).multiple is False

    def test_string_column_path_stored_until_resolved(self):
        flt = SelectWithSearchFilterNotInList(
            "collection.grant.name",
            "Grant",
            options=[("a", "A")],
        )
        assert flt.column == "collection.grant.name"
        assert flt.name == "Grant"
