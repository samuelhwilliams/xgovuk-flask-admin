# A "GOV.UK Frontend" theme for Flask-Admin

This package is designed to make it trivial to re-skin a [Flask-Admin](https://github.com/pallets-eco/flask-admin)
extension to have a consistent look and feel to many UK Government services, by using layouts, components and
patterns from the great [GOV.UK Design System](https://design-system.service.gov.uk/) (among other x-gov resources).

## Demo

![Image](https://github.com/user-attachments/assets/3592c49b-2d2c-44e9-8f49-bc52826c7373)

## How to integrate with Flask-Admin

Make sure your Flask app's Jinja environment is configured to load templates from at least the sources listed below.
Then initialise Flask-Admin and xgovuk-flask-admin appropriately, making sure to pass the X-GOV.UK Frontend Theme to
Flask-Admin.

```python
from flask import Flask
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader

from flask_admin import Admin
from xgovuk_flask_admin import XGovukFlaskAdmin
from xgovuk_flask_admin.theme import XGovukFrontendTheme

app = Flask(...)
app.jinja_options = {
  "loader": ChoiceLoader(
    [
      PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
      PrefixLoader({"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}),
      PackageLoader("xgovuk_flask_admin"),
    ]
  )
}

admin = Admin(app, theme=XGovukFrontendTheme())
xgovuk_flask_admin = XGovukFlaskAdmin(app)
```

### Writing model views

All of your SQLAlchemy model fields should derive from xgovuk-flask-admin's `XGovukModelView`, not from Flask-Admin's
`sqla.ModelView`.

To auto-generate CRUD pages for SQLAlchemy DB models, write sub-classes of XGovukModelView (which itself derives
from Flask-Admin's sqla.ModelView):

```python
from xgovuk_flask_admin import XGovukModelView

class UserModelView(XGovukModelView):
    page_size = 15
    can_create = True
    can_edit = True
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

```

And then attach these model views to the Flask-Admin instance:

```python
    flask_admin.add_view(UserModelView(User, db.session))
```

### Writing custom views

Create a new Jinja2 template that extends from "admin/master.html" (which is a proxy for admin/base.html). Generally
all you should need to implement is the `action_panel` block, like so:

```html
{% extends "admin/master.html" %}

{% block action_panel %}
<div class="govuk-grid-row">
  <div class="govuk-grid-column-two-thirds">
    <h1 class="govuk-heading-l">Custom view</h1>
    <p class="govuk-body">This is a custom view where you can do whatever you want.</p>
  </div>
</div>
{% endblock %}
```

And then define a class for the view in Python:
```python
from flask_admin import BaseView, expose

class CustomView(BaseView):
    @expose('/', methods=('GET',))
    def get(self):
        return self.render('custom_view.html')
```

And attach the view to your admin instance:

```python
flask_admin.add_view(CustomView(name="Custom View", endpoint="custom"))
```

## Recognition / attribution

This extension / theme has only been made possible by standing on a huge corpus of existing work across government,
including but not limited to:

- [GOV.UK Design System](https://design-system.service.gov.uk/)
- [Ministry of Justice Frontend](https://design-patterns.service.justice.gov.uk/)
- [GOV.UK Publishing Components](https://components.publishing.service.gov.uk/component-guide)
- HMLR's [govuk-frontend-jinja](https://github.com/LandRegistry/govuk-frontend-jinja) and [govuk-frontend-wtf]
  (https://github.com/LandRegistry/govuk-frontend-wtf) libraries

And, of course, [Flask-Admin](https://github.com/pallets-eco/flask-admin) itself.

## Compatibility

### Python

`xgovuk-flask-admin` will aim to be compatible with all supported versions of Python released from 2025, but this
package was put together in 2025 and I'm placing a lower bound of support on Python 3.12.

### Flask-Admin
Not all features of Flask-Admin are currently supported, or likely to be supported in the future.

| Feature                                    | Support status | Notes                                                                                                                                                                                                       |
|--------------------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Nested service navigation menu items       | 🔮             | Support Flask-Admin's "menu category" better, probably JS-only                                                                                                                                              |
| Create new records                         | ✅              |                                                                                                                                                                                                             |
| List existing records                      | ✅              |                                                                                                                                                                                                             |
| Keyword search when listing records        | ✅              |                                                                                                                                                                                                             |
| Apply filters when listing records         | ✅              |                                                                                                                                                                                                             |
| Sort results                               | ✅              |                                                                                                                                                                                                             |
| Changing page size when listing results    | ✅              |                                                                                                                                                                                                             |
| Custom page sizes                          | ✅              |                                                                                                                                                                                                             |
| Performing bulk actions on results         | ✅              |                                                                                                                                                                                                             |
| Editing record fields when listing results | 🤔             | Flask-Admin allows you to edit columns from the "list model" view; I'm not sure we want/need to support for this XGovuk-Flask-Admin when taking into account design+accessibility factors                   |
| View existing records                      | ✅              |                                                                                                                                                                                                             |
| Edit existing records                      | ✅              |                                                                                                                                                                                                             |
| Delete existing records                    | ✅              |                                                                                                                                                                                                             |
| Edit relationships                         | ✅              |                                                                                                                                                                                                             |
| Optimise/support 'large' relationships     | 🔮             | If a related table is large, performance will degrade rapidly because every related record is a choice in the select/dropdown menu. A future approach might be to dynamically load results from an API call |
| Edit date+datetime fields                  | ✅              |                                                                                                                                                                                                             |
| Edit one-to-one relationships              | ✅              |                                                                                                                                                                                                             |
| Edit one-to-many relationships             | ✅              |                                                                                                                                                                                                             |
| Standardised default GOV.UK error messages | 🔮             | It would be nice to have standard error messages for common validations, eg email format or dates                                                                                                           |
| Show full related model forms inline       | 🤔             | Flask-Admin allows rendering the full form of a related model inline of the main model (eg forms to edit posts by a user when editing a user). It might be nice to support this; some design thinking to do |

Please raise an issue in this repository if you need functionality from Flask-Admin that isn't supported yet.

### GOV.UK Frontend

`xgovuk-flask-admin` is packaged with compiled static assets that are served directly by the extension. This is a
technical constraint applied because `govuk-frontend-jinja` and `govuk-frontend-wtf` are themselves designed for
specific versions of GOV.UK Frontend.

Since `xgovuk-flask-admin` compiles assets from GOV.UK Frontend (and other x-gov frontend components), it will be
locked to specific versions of `govuk-frontend-jinja` and `govuk-frontend-wtf`.

It may be possible to compile bundles for various versions of GOV.UK Frontend, in order to support various
combinations of `govuk-frontend-jinja` and `govuk-frontend-wtf` in the future, but this is not currently planned.
Please comment on https://github.com/samuelhwilliams/xgovuk-flask-admin/issues/1 if this would be useful.

The latest release of `xgovuk-flask-admin` will generally track the latest releases of GOV.UK Frontend,
`govuk-frontend-jinja`, and `govuk-frontend-wtf`.

| Package              | GOV.UK Frontend | govuk-frontend-jinja | govuk-frontend-wtf |
|----------------------|-----------------|----------------------|--------------------|
| >=0.1.0              | 5.12.0          | 3.8.0                | 3.2.0              |

`xgovuk-flask-admin` uses `govuk-colour("purple")` as its brand colour on the (somewhat unfounded/unresearched) belief
that this isn't a colour used for branding in many places, so it's broadly "available". Given it will be unfamiliar, it
visually signifies that you're in an unusual (read: privileged) interface. Because we pre-compile assets, we need to
choose **some** colour, and I wanted to avoid black, GOV.UK blue, or common brands. Please comment on https://github.
com/samuelhwilliams/xgovuk-flask-admin/issues/7 if customisation/extension is needed.

Because this theme uses common, well-tested components from across UK Government, it should be reasonably accessible
out of the box and will generally be progressively enhanced (ie functional without javascript). However, some
components used in xgovuk-flask-admin are not 'officially' fully supported or fully accessible, and xgovuk-flask-admin
applies some customisation to styling and interactions on some components in order to work with Flask-Admin and
provide a (hopefully) more usable design and experience.
