from flask import Blueprint, current_app, send_from_directory

files_blueprint = Blueprint('files', 'skylines')


@files_blueprint.route('/<path:filename>')
def index(filename):
    path = current_app.config.get('SKYLINES_FILES_PATH')
    return send_from_directory(path, filename)
