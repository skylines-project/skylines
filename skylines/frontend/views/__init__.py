from .errors import register as register_error_handlers
from .i18n import register as register_i18n
from .login import register as register_login

from .about import about_blueprint
from .airport import airport_blueprint
from .aircraft_models import aircraft_models_blueprint
from .assets import assets_blueprint
from .club import club_blueprint
from .clubs import clubs_blueprint
from .files import files_blueprint
from .flight import flight_blueprint
from .flights import flights_blueprint
from .livetrack24 import lt24_blueprint
from .notifications import notifications_blueprint
from .ranking import ranking_blueprint
from .search import search_blueprint
from .settings import settings_blueprint
from .statistics import statistics_blueprint
from .timeline import timeline_blueprint
from .track import track_blueprint
from .tracking import tracking_blueprint
from .upload import upload_blueprint
from .user import user_blueprint
from .users import users_blueprint
from .widgets import widgets_blueprint


def register(app):
    register_error_handlers(app)
    register_i18n(app)
    register_login(app)

    app.register_blueprint(about_blueprint)
    app.register_blueprint(airport_blueprint)
    app.register_blueprint(aircraft_models_blueprint)
    app.register_blueprint(assets_blueprint)
    app.register_blueprint(club_blueprint)
    app.register_blueprint(clubs_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(flight_blueprint)
    app.register_blueprint(flights_blueprint)
    app.register_blueprint(lt24_blueprint)
    app.register_blueprint(notifications_blueprint)
    app.register_blueprint(ranking_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(statistics_blueprint)
    app.register_blueprint(timeline_blueprint)
    app.register_blueprint(track_blueprint)
    app.register_blueprint(tracking_blueprint)
    app.register_blueprint(upload_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(widgets_blueprint)
