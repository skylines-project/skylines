from flask import Blueprint, current_app, send_from_directory

assets_blueprint = Blueprint('assets', 'skylines')


@assets_blueprint.route('/<path:filename>')
def static(filename):
    return send_from_directory(current_app.config.get('ASSETS_LOAD_DIR'), filename)


@assets_blueprint.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(current_app.config.get('ASSETS_DIRECTORY'), filename)
