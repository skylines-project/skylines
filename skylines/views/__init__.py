from skylines.views.i18n import register as register_i18n
from skylines.views.login import register as register_login

from skylines.views.about import about_blueprint, about
from skylines.views.api import api_blueprint
from skylines.views.assets import assets_blueprint
from skylines.views.club import club_blueprint
from skylines.views.clubs import clubs_blueprint
from skylines.views.files import files_blueprint
from skylines.views.flight import flight_blueprint
from skylines.views.flights import flights_blueprint
from skylines.views.livetrack24 import lt24_blueprint
from skylines.views.notifications import notifications_blueprint
from skylines.views.ranking import ranking_blueprint
from skylines.views.search import search_blueprint
from skylines.views.settings import settings_blueprint
from skylines.views.statistics import statistics_blueprint
from skylines.views.timeline import timeline_blueprint
from skylines.views.track import track_blueprint
from skylines.views.tracking import tracking_blueprint
from skylines.views.upload import upload_blueprint
from skylines.views.user import user_blueprint
from skylines.views.users import users_blueprint
from skylines.views.widgets import widgets_blueprint


def register(app):
    register_i18n(app)
    register_login(app)

    app.register_blueprint(about_blueprint, url_prefix='/about')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(assets_blueprint)
    app.register_blueprint(club_blueprint, url_prefix='/clubs/<club_id>')
    app.register_blueprint(clubs_blueprint, url_prefix='/clubs')
    app.register_blueprint(files_blueprint, url_prefix='/files')
    app.register_blueprint(flight_blueprint, url_prefix='/flights/<flight_id>')
    app.register_blueprint(flights_blueprint, url_prefix='/flights')
    app.register_blueprint(lt24_blueprint)
    app.register_blueprint(notifications_blueprint, url_prefix='/notifications')
    app.register_blueprint(ranking_blueprint, url_prefix='/ranking')
    app.register_blueprint(search_blueprint, url_prefix='/search')
    app.register_blueprint(settings_blueprint, url_prefix='/settings')
    app.register_blueprint(statistics_blueprint, url_prefix='/statistics')
    app.register_blueprint(timeline_blueprint, url_prefix='/timeline')
    app.register_blueprint(track_blueprint, url_prefix='/tracking/<user_id>')
    app.register_blueprint(tracking_blueprint, url_prefix='/tracking')
    app.register_blueprint(upload_blueprint, url_prefix='/flights/upload')
    app.register_blueprint(user_blueprint, url_prefix='/users/<user_id>')
    app.register_blueprint(users_blueprint, url_prefix='/users')
    app.register_blueprint(widgets_blueprint, url_prefix='/widgets')

    @app.route('/')
    def index():
        return about()
