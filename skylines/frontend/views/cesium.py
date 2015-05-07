from flask import Blueprint, current_app, send_from_directory
import os

cesium_blueprint = Blueprint('cesium', 'skylines')


@cesium_blueprint.route('/<path:filename>')
def index(filename):
    path = current_app.config.get('SKYLINES_CESIUM_PATH')
    path += '/' + os.path.dirname(filename) + '/'
    filename = os.path.basename(filename)

    return send_from_directory(path, filename)
