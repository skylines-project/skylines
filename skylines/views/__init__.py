from flask import redirect, url_for

from skylines import app

import skylines.views.i18n
import skylines.views.login
import skylines.views.search

from skylines.views.about import about_blueprint
from skylines.views.api import api_blueprint
from skylines.views.clubs import clubs_blueprint
from skylines.views.flight import flight_blueprint
from skylines.views.flights import flights_blueprint
from skylines.views.notifications import notifications_blueprint
from skylines.views.ranking import ranking_blueprint
from skylines.views.statistics import statistics_blueprint
from skylines.views.upload import upload_blueprint
from skylines.views.user import user_blueprint
from skylines.views.users import users_blueprint

app.register_blueprint(about_blueprint, url_prefix='/about')
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(clubs_blueprint, url_prefix='/clubs')
app.register_blueprint(flight_blueprint, url_prefix='/flights/<flight_id>')
app.register_blueprint(flights_blueprint, url_prefix='/flights')
app.register_blueprint(notifications_blueprint, url_prefix='/notifications')
app.register_blueprint(ranking_blueprint, url_prefix='/ranking')
app.register_blueprint(statistics_blueprint, url_prefix='/statistics')
app.register_blueprint(upload_blueprint, url_prefix='/flights/upload')
app.register_blueprint(user_blueprint, url_prefix='/users/<user_id>')
app.register_blueprint(users_blueprint, url_prefix='/users')


@app.route('/')
def index():
    return redirect(url_for('flights.latest'))
