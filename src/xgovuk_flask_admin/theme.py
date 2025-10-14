from dataclasses import dataclass

from flask_admin.theme import Theme


@dataclass
class XGovukFrontendTheme(Theme):
    folder: str = "admin"
    base_template: str = "admin/base.html"
