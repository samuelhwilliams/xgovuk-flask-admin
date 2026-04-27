"""Unit tests for SelectWithSearchFilter."""

from unittest.mock import MagicMock

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from xgovuk_flask_admin.filters import SelectWithSearchFilter

Base = declarative_base()


class SampleModel(Base):
    __tablename__ = "swsf_sample"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)


class TestSelectWithSearchFilter:
    def _make(self, **overrides):
        defaults = {
            "column": SampleModel.name,
            "name": "Name",
            "predicate_builder": lambda col, value: col == value,
            "options": [("a", "A"), ("b", "B")],
        }
        defaults.update(overrides)
        return SelectWithSearchFilter(**defaults)

    def test_data_type_marks_select_with_search(self):
        flt = self._make()
        assert flt.data_type == "select-with-search"

    def test_default_operation_is_is(self):
        flt = self._make()
        assert flt.operation() == "is"

    def test_custom_operation_name(self):
        flt = self._make(operation_name="matches")
        assert flt.operation() == "matches"

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

    def test_clean_single_select_passthrough(self):
        flt = self._make(multiple=False)
        assert flt.clean("hello") == "hello"

    def test_clean_multi_select_string_split(self):
        flt = self._make(multiple=True)
        assert flt.clean("a,b,c") == ["a", "b", "c"]

    def test_clean_multi_select_strips_empties(self):
        flt = self._make(multiple=True)
        assert flt.clean("a, ,b,") == ["a", "b"]

    def test_clean_multi_select_list_passthrough(self):
        flt = self._make(multiple=True)
        assert flt.clean(["a", "b"]) == ["a", "b"]

    def test_clean_multi_select_wraps_scalar(self):
        flt = self._make(multiple=True)
        assert flt.clean(42) == [42]

    def test_apply_calls_predicate_builder_with_column_and_value(self):
        captured = {}

        def predicate(col, value):
            captured["col"] = col
            captured["value"] = value
            return col == value

        flt = self._make(predicate_builder=predicate)

        query = MagicMock()
        flt.apply(query, "alice")

        assert captured["value"] == "alice"
        assert captured["col"] is SampleModel.name
        query.filter.assert_called_once()

    def test_apply_uses_aliased_column(self):
        captured = {}

        def predicate(col, value):
            captured["col"] = col
            return col == value

        flt = self._make(predicate_builder=predicate)

        alias = MagicMock()
        alias.name = "aliased"
        query = MagicMock()
        flt.apply(query, "v", alias=alias)

        assert captured["col"] is alias.name

    def test_multiple_flag_stored(self):
        assert self._make(multiple=True).multiple is True
        assert self._make(multiple=False).multiple is False
