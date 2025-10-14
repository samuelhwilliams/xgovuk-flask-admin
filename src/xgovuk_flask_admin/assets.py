import json
from pathlib import Path
from textwrap import dedent

from flask import url_for

ROOT_DIR = Path(__file__).parent


def xgovuk_flask_admin_include_css():
    manifest_file = ROOT_DIR / "static" / "dist" / "manifest.json"

    with open(manifest_file) as f:
        manifest = json.load(f)

    css_file = Path(manifest["src/assets/main.scss"]["file"]).name
    css_file_url = url_for("xgovuk_flask_admin.static", filename=css_file)

    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <link rel="stylesheet" href="{css_file_url}">
        """
    ).strip()


def xgovuk_flask_admin_include_js():
    manifest_file = ROOT_DIR / "static" / "dist" / "manifest.json"

    with open(manifest_file) as f:
        manifest = json.load(f)

    js_file = Path(manifest["src/assets/main.js"]["file"]).name
    js_file_url = url_for("xgovuk_flask_admin.static", filename=js_file)

    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="{js_file_url}"></script>
        """
    ).strip()
