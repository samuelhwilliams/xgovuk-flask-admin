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
