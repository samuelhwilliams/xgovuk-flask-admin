"""Integration tests for SelectWithSearchFilterInList and SelectWithSearchFilterNotInList."""

import pytest

from example.models import Post
from tests.factories import PostFactory, UserFactory
from xgovuk_flask_admin.filters import (
    SelectWithSearchFilterInList,
    SelectWithSearchFilterNotInList,
)


@pytest.fixture
def filter_test_data(db_session):
    alice = UserFactory(email="alice@example.com")
    bob = UserFactory(email="bob@example.com")
    db_session.flush()

    PostFactory(title="Alice 1", author=alice)
    PostFactory(title="Alice 2", author=alice)
    PostFactory(title="Bob 1", author=bob)
    db_session.flush()

    return alice, bob


@pytest.mark.integration
class TestSelectWithSearchFilterInListApply:
    def test_single_value_filters_query(self, db_session, filter_test_data):
        alice, _ = filter_test_data
        flt = SelectWithSearchFilterInList(
            Post.author_id,
            name="Author",
            options=lambda: [],
        )

        query = db_session.query(Post)
        cleaned = flt.clean(str(alice.id))
        filtered = flt.apply(query, cleaned)

        titles = sorted(p.title for p in filtered.all())
        assert titles == ["Alice 1", "Alice 2"]

    def test_multi_value_filters_query(self, db_session, filter_test_data):
        alice, bob = filter_test_data
        flt = SelectWithSearchFilterInList(
            Post.author_id,
            name="Author",
            options=lambda: [],
            multiple=True,
        )

        query = db_session.query(Post)
        cleaned = flt.clean(f"{alice.id},{bob.id}")
        filtered = flt.apply(query, cleaned)

        assert filtered.count() == 3


@pytest.mark.integration
class TestSelectWithSearchFilterNotInListApply:
    def test_single_value_excludes_match(self, db_session, filter_test_data):
        alice, bob = filter_test_data
        flt = SelectWithSearchFilterNotInList(
            Post.author_id,
            name="Author",
            options=lambda: [],
        )

        query = db_session.query(Post)
        cleaned = flt.clean(str(alice.id))
        filtered = flt.apply(query, cleaned)

        titles = sorted(p.title for p in filtered.all())
        assert titles == ["Bob 1"]

    def test_multi_value_excludes_all_matches(self, db_session, filter_test_data):
        alice, bob = filter_test_data
        flt = SelectWithSearchFilterNotInList(
            Post.author_id,
            name="Author",
            options=lambda: [],
            multiple=True,
        )

        query = db_session.query(Post)
        cleaned = flt.clean(f"{alice.id},{bob.id}")
        filtered = flt.apply(query, cleaned)

        assert filtered.count() == 0


@pytest.mark.integration
class TestSelectWithSearchFilterOptionsRefresh:
    def test_options_reflect_current_db_state_per_render(
        self, client, db_session, filter_test_data
    ):
        alice, _ = filter_test_data

        first_response = client.get("/admin/post/")
        assert first_response.status_code == 200
        first_html = first_response.data.decode("utf-8")
        assert "alice@example.com" in first_html

        UserFactory(email="charlie@example.com")
        db_session.flush()

        second_response = client.get("/admin/post/")
        assert second_response.status_code == 200
        second_html = second_response.data.decode("utf-8")
        assert "charlie@example.com" in second_html

    def test_filter_form_uses_select_with_search_widget(self, client, filter_test_data):
        response = client.get("/admin/post/")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        assert 'data-module="select-with-search"' in html
        assert "alice@example.com" in html
        assert "bob@example.com" in html

    def test_applying_filter_via_url_filters_listing(
        self, client, db_session, filter_test_data
    ):
        alice, bob = filter_test_data

        response = client.get(f"/admin/post/?flt0_0={alice.id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        assert "Alice 1" in html
        assert "Alice 2" in html
        assert "Bob 1" not in html

    def test_active_filter_tag_shows_label_not_value(
        self, client, db_session, filter_test_data
    ):
        alice, _ = filter_test_data

        response = client.get(f"/admin/post/?flt0_0={alice.id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        tag_start = html.find('class="moj-filter__tag"')
        assert tag_start > 0
        tag_end = html.find("</a>", tag_start)
        tag_html = html[tag_start:tag_end]

        assert "alice@example.com" in tag_html
        assert f"is: {alice.id}<" not in tag_html and f"is: {alice.id} " not in tag_html
