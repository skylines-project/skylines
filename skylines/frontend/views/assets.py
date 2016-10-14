from flask import Blueprint, current_app, send_from_directory

assets_blueprint = Blueprint('assets', 'skylines')


@assets_blueprint.route('/<path:filename>')
def static(filename):
    return send_from_directory(current_app.config.get('ASSETS_LOAD_DIR'), filename)
