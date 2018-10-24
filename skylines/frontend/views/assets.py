import os.path

from flask import Blueprint, current_app, send_from_directory, send_file
from werkzeug.exceptions import NotFound

assets_blueprint = Blueprint("assets", "skylines")


@assets_blueprint.route("/")
@assets_blueprint.route("/<path:path>")
def static(**kwargs):
    path = kwargs.get("path", "")
    assets_folder = current_app.config.get("ASSETS_LOAD_DIR")
    try:
        return send_from_directory(assets_folder, path)
    except NotFound:
        return send_file(os.path.join(assets_folder, "index.html"))
