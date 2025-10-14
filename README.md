# A "GOV.UK Frontend" theme for Flask-Admin

This package is designed to make it trivial to re-skin a [Flask-Admin](https://github.com/pallets-eco/flask-admin) 
extension to have a consistent look and feel to many UK Government services, by using layouts, components and 
patterns from the great [GOV.UK Design System](https://design-system.service.gov.uk/) (among other x-gov resources).

## Demo

![Image](https://github.com/user-attachments/assets/3592c49b-2d2c-44e9-8f49-bc52826c7373)

## How to integrate with Flask-Admin

Make sure your Flask app's Jinja environment is configured to load templates from at least the sources listed below.
Then initialise Flask-Admin and xgovuk-flask-admin appropriately, making sure to pass the GOV.UK Frontend Theme to
Flask-Admin.

```python
from flask import Flask
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader

from flask_admin import Admin
from xgovuk_flask_admin import XGovukFlaskAdmin, XGovukFrontendTheme

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

All of your SQLAlchemy model fields should derive from xgovuk-flask-admin's `XGovukModelView`, not from Flask-Admin's
`sqla.ModelView`.

## Recognition / attribution

This extension / theme has only been made possible by standing on a huge corpus of existing work across government, 
including but not limited to:

- [GOV.UK Design System](https://design-system.service.gov.uk/)
- [Ministry of Justice Frontend](https://design-patterns.service.justice.gov.uk/)
- [Accessible autocomplete](https://alphagov.github.io/accessible-autocomplete/examples/)
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

| Feature                                    | Support status | Notes                                                                                                                                                                                                         |
|--------------------------------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Nested service navigation menu items       | 🔮             | Support Flask-Admin's "menu category" better, probably JS-only                                                                                                                                                |
| Create new records                         | ✅              |                                                                                                                                                                                                               |
| List existing records                      | ✅              |                                                                                                                                                                                                               |
| Keyword search when listing records        | ✅              |                                                                                                                                                                                                               |
| Apply filters when listing records         | ✅              |                                                                                                                                                                                                               |
| Sort results                               | ✅              |                                                                                                                                                                                                               |
| Changing page size when listing results    | ✅              |                                                                                                                                                                                                               |
| Custom page sizes                          | ✅              |                                                                                                                                                                                                               |
| Performing bulk actions on results         | ✅              |                                                                                                                                                                                                               |
| View existing records                      | ✅              |                                                                                                                                                                                                               |
| Edit existing records                      | ✅              |                                                                                                                                                                                                               |
| Delete existing records                    | ✅              |                                                                                                                                                                                                               |
| Edit relationships                         | ✅              |                                                                                                                                                                                                               |
| Optimise/support 'large' relationships     | 🔮             | If a related table is large, performance will degrade rapidly because every related record is a choice in the select/dropdown menu. A future approach might be to dynamically load results from an API call   | 
| Edit date+datetime fields                  | ✅              |                                                                                                                                                                                                               |
| Edit one-to-one relationships              | ✅              |                                                                                                                                                                                                               |
| Edit one-to-many relationships             | ✅              |                                                                                                                                                                                                               |
| Standardised default GOV.UK error messages | 🔮             |                                                                                                                                                                                                               | 
| Show full related model forms inline       | 🤔             | Flask-Admin allows rendering the full form of a related model inline of the main model (eg forms to edit posts by a user when editing a user). It might be nice to support this; some design thinking to do   |

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

The latest release of `xgovuk-flask-admin` will generally track the latest release of GOV.UK Frontend, 
`govuk-frontend-jinja`, and `govuk-frontend-wtf`.

| Package              | Currently supported version |
|----------------------|-----------------------------|
| GOV.UK Frontend      | 5.12.0                      |
| govuk-frontend-jinja | 3.8.0                       |
| govuk-frontend-wtf   | 3.2.0                       |

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

## Developing this extension

### Running tests

Tests can be run against multiple Python versions (eg 3.13 and 3.14) using tox. The test suite is split into 
unit/integration tests and e2e tests to avoid async loop conflicts with playwright:

```bash
# Run all tests (unit, integration, and e2e) across all Python versions
uv run tox

# Run only unit and integration tests
uv run tox -e py313,py314

# Run only e2e tests
uv run tox -e py313-e2e,py314-e2e

# Run tests for a specific Python version
uv run tox -e py313           # unit + integration only
uv run tox -e py313-e2e       # e2e only
```

### Rebuilding GOV.UK Frontend assets

GOV.UK Flask Admin uses and extends the GOV.UK Frontend CSS and JS in order to add functionality required to display 
information and action dense admin pages.

These assets are compiled using Flask-Vite.

#### One-off setup

1. Install Node LTS (currently v20)
2. Run `flask vite install`
3. Run `flask vite build` to compile GOV.UK Frontend assets and copy them into `xgovuk_flask_admin/static`
4. Commit the newly compiled assets.

### Doing a release

There is a publishing workflow set up through GitHub actions. To do a release:

- Use `uv version <new version #>` to update the xgovuk-flask-admin's version
- Create a changelog entry in CHANGELOG.md recording breaking changes, new features, bug fixes, etc.
- Commit and push this change on a branch `release/v<x.y.z>` to GitHub. Open a PR.
- Once CI tests are green, create a tag for that commit in git: `git tag v<x.y.z>`.
- Push it to GitHub and the publishing workflow will build the distribution and prepare a GitHub release.
- Update the release notes in GitHub.
- Manually approve the publishing workflow to push the release to PyPi.
- Publish the GitHub release note.
