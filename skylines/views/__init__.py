from flask import redirect

from skylines import app
from skylines.model import User

import skylines.views.i18n
import skylines.views.login
import skylines.views.search

from skylines.views.about import about_blueprint
from skylines.views.api import api_blueprint
from skylines.views.statistics import statistics_blueprint
from skylines.views.ranking import ranking_blueprint

app.register_blueprint(about_blueprint, url_prefix='/about')
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(ranking_blueprint, url_prefix='/ranking')
app.register_blueprint(statistics_blueprint, url_prefix='/statistics')


@app.route('/')
def index():
    return redirect('/flights/latest')


@app.route('/users/')
def user_list():
    return ', '.join([user.name for user in User.query()])
