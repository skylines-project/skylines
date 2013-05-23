from flask import Flask, g
from flask.ext.babel import Babel, get_locale
from flask.ext.assets import Environment
from webassets.loaders import PythonLoader
from skylines.lib import helpers


def create_app():
    app = Flask(__name__, static_folder='public')
    app.config.from_object('skylines.config.default')

    babel = Babel(app)

    bundles = PythonLoader('skylines.assets.bundles').load_bundles()
    assets = Environment(app)

    load_path = app.config.get('ASSETS_LOAD_DIR', None)
    if load_path is not None:
        load_url = app.config.get('ASSETS_LOAD_URL', None)
        assets.append_path(load_path, load_url)

    assets.register(bundles)

    return app

app = create_app()

import skylines.views

@app.before_request
def inject_active_locale():
    g.available_locales = app.babel_instance.list_translations()
    g.active_locale = get_locale()

@app.context_processor
def inject_helpers_lib():
    return dict(h=helpers)

@app.context_processor
def inject_template_context():
    return dict(c=g)
