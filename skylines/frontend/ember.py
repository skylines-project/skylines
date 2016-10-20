import os.path

from flask import current_app, send_file


def send_index():
    return send_file(os.path.join(current_app.config.get('ASSETS_LOAD_DIR'), 'index.html'))
