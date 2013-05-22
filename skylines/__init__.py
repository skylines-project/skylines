from flask import Flask
from flask.ext.babel import Babel
app = Flask(__name__, static_folder='public')
babel = Babel(app)

import skylines.views
