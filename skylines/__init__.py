from flask import Flask
from flask.ext.babel import Babel
from flask.ext.assets import Environment

app = Flask(__name__, static_folder='public')
babel = Babel(app)
assets = Environment(app)

import skylines.views
