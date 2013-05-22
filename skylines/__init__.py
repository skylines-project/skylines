from flask import Flask
from flask.ext.babel import Babel
from flask.ext.assets import Environment


def create_app():
    app = Flask(__name__, static_folder='public')
    babel = Babel(app)
    assets = Environment(app)
    return app

app = create_app()

import skylines.views
