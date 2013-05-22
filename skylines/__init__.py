from flask import Flask
from flask.ext.babel import Babel
from flask.ext.assets import Environment
from webassets.loaders import PythonLoader


def create_app():
    app = Flask(__name__, static_folder='public')
    babel = Babel(app)

    bundles = PythonLoader('skylines.assets.bundles').load_bundles()
    assets = Environment(app)
    assets.register(bundles)

    return app

app = create_app()

import skylines.views
