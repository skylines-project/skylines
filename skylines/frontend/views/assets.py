from flask import Blueprint, current_app, send_from_directory
from werkzeug.exceptions import NotFound

from skylines.frontend.ember import send_index

assets_blueprint = Blueprint('assets', 'skylines')


@assets_blueprint.route('/')
@assets_blueprint.route('/<path:path>')
def static(**kwargs):
    path = kwargs.get('path', '')
    try:
        return send_from_directory(current_app.config.get('ASSETS_LOAD_DIR'), path)
    except NotFound:
        return send_index()
