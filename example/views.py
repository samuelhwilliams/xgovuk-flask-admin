from flask_admin import BaseView, expose
from wtforms.validators import Email

from xgovuk_flask_admin import XGovukModelView


class UserModelView(XGovukModelView):
    page_size = 15
    can_set_page_size = True
    page_size_options = [10, 15, 25, 50]

    form_args = {"email": {"validators": [Email()]}}

    column_filters = [
        "age",
        "job",
        "email",
        "created_at",
        "favourite_colour",
        "last_logged_in_at",
    ]

    column_searchable_list = ["email", "name"]

    can_export = True
    export_types = ["csv"]

    column_descriptions = {
        "age": "User's age in years",
        "email": "Email address for contacting the user",
        "created_at": "Date the user account was created",
        "last_logged_in_at": "Date and time of the user's last login",
    }


class PostModelView(XGovukModelView):
    page_size = 20
    can_set_page_size = True
    can_edit = False
    can_view_details = True

    column_filters = ["author", "published_at", "created_at"]

    column_searchable_list = ["title", "content"]

    column_list = ["id", "title", "author", "published_at", "created_at"]

    column_descriptions = {
        "author": "The user who wrote this post",
        "published_at": "Date and time the post was published (empty for drafts)",
        "created_at": "Date and time the post was created",
    }

    column_formatters = {"author": lambda v, c, m, p: m.author.name if m.author else ""}


class AccountModelView(XGovukModelView):
    column_list = ["id", "user.email"]


class CustomView(BaseView):
    @expose('/', methods=('GET',))
    def index(self):
        return self.render('custom_view.html')
