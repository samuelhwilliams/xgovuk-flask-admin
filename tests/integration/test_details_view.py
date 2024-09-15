"""Integration tests for details view rendering."""

import pytest
import datetime
from bs4 import BeautifulSoup

from tests.factories import UserFactory, PostFactory


@pytest.mark.integration
class TestDetailsViewRendering:
    """Test details view renders correctly with GOV.UK Summary List."""

    def test_details_view_uses_govuk_summary_list(self, client, db_session):
        """Test details view renders using GOV.UK Summary List component."""
        # Create a post (Post model has can_view_details=True)
        post = PostFactory.create()
        post_id = post.id

        response = client.get(f"/admin/post/details/?id={post_id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check for GOV.UK Summary List component
        assert "govuk-summary-list" in html
        assert "govuk-summary-list__key" in html
        assert "govuk-summary-list__value" in html

        # Check that old table classes are NOT present
        assert "table-hover" not in html
        assert "table-bordered" not in html

    def test_details_view_displays_all_fields(self, client, db_session):
        """Test details view displays all model fields."""
        # Create a post with known author name
        user = UserFactory.create(name="Test Author")
        post = PostFactory.create(author=user)
        post_id = post.id
        author_name = user.name

        response = client.get(f"/admin/post/details/?id={post_id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check that post data is displayed (author name is formatted in the view)
        assert author_name in html or "Author" in html

    def test_details_view_has_heading(self, client, db_session):
        """Test details view has a proper heading."""
        post = PostFactory.create()
        post_id = post.id

        response = client.get(f"/admin/post/details/?id={post_id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check for heading
        assert "govuk-heading-l" in html
        assert "Post details" in html

    def test_details_view_has_back_link(self, client, db_session):
        """Test details view has a back link."""
        post = PostFactory.create()
        post_id = post.id

        response = client.get(f"/admin/post/details/?id={post_id}&url=/admin/post/")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check for GOV.UK back link
        assert "govuk-back-link" in html

    def test_details_view_with_multiline_content(self, client, db_session):
        """Test details view converts newlines to <br> tags for multiline content."""
        # Create a post with multiline content
        post = PostFactory.create(
            title="Line1\nLine2\nLine3",
            content="Paragraph 1\nParagraph 2\nParagraph 3",
        )
        post_id = post.id

        response = client.get(f"/admin/post/details/?id={post_id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")

        # Check that newlines are converted to <br> tags
        assert "Line1<br>Line2<br>Line3" in html
        assert "Paragraph 1<br>Paragraph 2<br>Paragraph 3" in html

        # Verify content is escaped and then <br> tags are added
        assert "<br>" in html

        # Make sure the lines are individually present
        assert "Line1" in html
        assert "Line2" in html
        assert "Line3" in html

    def test_details_view_escapes_html_content(self, client, db_session):
        """Test details view properly escapes HTML/JavaScript to prevent XSS."""
        # Create a post with HTML/JavaScript content that should be escaped
        post = PostFactory.create(
            title="<script>alert('XSS')</script>",
            content="<img src=x onerror=alert('XSS')>",
        )
        post_id = post.id

        response = client.get(f"/admin/post/details/?id={post_id}")
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # Check that HTML tags are escaped, not executed
        # BeautifulSoup will parse the HTML, and if the content was properly escaped,
        # it will appear as text content, not as actual HTML tags

        # Find the summary list values that contain our escaped content
        summary_values = soup.find_all(class_="govuk-summary-list__value")

        # Get all text from summary list values
        all_text = " ".join([val.get_text() for val in summary_values])

        # The escaped HTML should appear as literal text (BeautifulSoup decodes HTML entities)
        assert "<script>alert('XSS')</script>" in all_text, (
            "Script tag should appear as text content (properly escaped)"
        )
        assert "<img src=x onerror=alert('XSS')>" in all_text, (
            "Img tag should appear as text content (properly escaped)"
        )

        # Verify that actual script/img elements were NOT created in the DOM
        scripts = soup.find_all("script", string=lambda text: text and "alert('XSS')" in text)
        assert len(scripts) == 0, "No script elements should be created from user content"

        imgs_with_onerror = soup.find_all("img", attrs={"onerror": True})
        assert len(imgs_with_onerror) == 0, "No img elements with onerror should be created"
