from .errors import register as register_error_handlers

from .about import about_blueprint
from .airports import airports_blueprint
from .aircraft_models import aircraft_models_blueprint
from .assets import assets_blueprint
from .clubs import clubs_blueprint
from .files import files_blueprint
from .flight import flight_blueprint
from .flights import flights_blueprint
from .i18n import i18n_blueprint
from .livetrack24 import lt24_blueprint
from .mapitems import mapitems_blueprint
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

    app.register_blueprint(assets_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(lt24_blueprint)
    app.register_blueprint(widgets_blueprint)

    app.register_blueprint(about_blueprint, url_prefix='/api')
    app.register_blueprint(airports_blueprint, url_prefix='/api')
    app.register_blueprint(aircraft_models_blueprint, url_prefix='/api')
    app.register_blueprint(clubs_blueprint, url_prefix='/api')
    app.register_blueprint(flight_blueprint, url_prefix='/api')
    app.register_blueprint(flights_blueprint, url_prefix='/api')
    app.register_blueprint(i18n_blueprint, url_prefix='/api')
    app.register_blueprint(mapitems_blueprint, url_prefix='/api')
    app.register_blueprint(notifications_blueprint, url_prefix='/api')
    app.register_blueprint(ranking_blueprint, url_prefix='/api')
    app.register_blueprint(search_blueprint, url_prefix='/api')
    app.register_blueprint(settings_blueprint, url_prefix='/api')
    app.register_blueprint(statistics_blueprint, url_prefix='/api')
    app.register_blueprint(timeline_blueprint, url_prefix='/api')
    app.register_blueprint(track_blueprint, url_prefix='/api')
    app.register_blueprint(tracking_blueprint, url_prefix='/api')
    app.register_blueprint(upload_blueprint, url_prefix='/api')
    app.register_blueprint(user_blueprint, url_prefix='/api')
    app.register_blueprint(users_blueprint, url_prefix='/api')
