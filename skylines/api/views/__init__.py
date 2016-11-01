from flask import request
from werkzeug.exceptions import Forbidden
from werkzeug.useragents import UserAgent

from skylines.api.cors import cors

from skylines.api.views.about import about_blueprint
from skylines.api.views.airports import airports_blueprint
from skylines.api.views.aircraft_models import aircraft_models_blueprint
from skylines.api.views.clubs import clubs_blueprint
from skylines.api.views.flights import flights_blueprint
from skylines.api.views.i18n import i18n_blueprint
from skylines.api.views.mapitems import mapitems_blueprint
from skylines.api.views.notifications import notifications_blueprint
from skylines.api.views.ranking import ranking_blueprint
from skylines.api.views.search import search_blueprint
from skylines.api.views.settings import settings_blueprint
from skylines.api.views.statistics import statistics_blueprint
from skylines.api.views.timeline import timeline_blueprint
from skylines.api.views.tracking import tracking_blueprint
from skylines.api.views.upload import upload_blueprint
from skylines.api.views.users import users_blueprint


def register(app):
    """
    :param flask.Flask app: a Flask app
    """

    from .errors import register as register_error_handlers

    @app.before_request
    def require_user_agent():
        """
        API requests require a ``User-Agent`` header
        """
        user_agent = request.user_agent
        assert isinstance(user_agent, UserAgent)

        if not user_agent.string:
            description = 'You don\'t have the permission to access the API with a User-Agent header.'
            raise Forbidden(description)

    cors.init_app(app)

    register_error_handlers(app)

    app.register_blueprint(about_blueprint)
    app.register_blueprint(airports_blueprint)
    app.register_blueprint(aircraft_models_blueprint)
    app.register_blueprint(clubs_blueprint)
    app.register_blueprint(flights_blueprint)
    app.register_blueprint(i18n_blueprint)
    app.register_blueprint(mapitems_blueprint)
    app.register_blueprint(notifications_blueprint)
    app.register_blueprint(ranking_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(statistics_blueprint)
    app.register_blueprint(timeline_blueprint)
    app.register_blueprint(tracking_blueprint)
    app.register_blueprint(upload_blueprint)
    app.register_blueprint(users_blueprint)
