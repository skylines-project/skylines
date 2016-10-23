import os.path

from flask import Blueprint, current_app, jsonify

from skylines.frontend.ember import send_index

about_blueprint = Blueprint('about', 'skylines')


@about_blueprint.route('/about')
@about_blueprint.route('/about/<path:path>')
def about(**kwargs):
    return send_index()


@about_blueprint.route('/api/imprint')
def imprint():
    content = current_app.config.get(
        'SKYLINES_IMPRINT',
        'Please set the `SKYLINES_IMPRINT` variable in the config file.')

    return jsonify(content=content)


@about_blueprint.route('/api/team')
def skylines_team():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', '..', '..', 'AUTHORS.md')
    with open(path) as f:
        content = f.read().decode('utf-8')

    return jsonify(content=content)


@about_blueprint.route('/api/license')
def license():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', '..', '..', 'LICENSE')
    with open(path) as f:
        content = f.read().decode('utf-8')

    return jsonify(content=content)
