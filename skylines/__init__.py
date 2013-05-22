from flask import Flask, g
from flask.ext.babel import Babel
from flask.ext.assets import Environment
from webassets.loaders import PythonLoader
from skylines.lib import helpers


def create_app():
    app = Flask(__name__, static_folder='public')
    babel = Babel(app)

    bundles = PythonLoader('skylines.assets.bundles').load_bundles()
    assets = Environment(app)
    assets.register(bundles)

    return app

app = create_app()

import skylines.views

@app.context_processor
def inject_helpers_lib():
    return dict(h=helpers)

@app.context_processor
def inject_template_context():
    return dict(c=g)
