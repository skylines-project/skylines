from flask import request
from werkzeug.useragents import UserAgent
from .errors import register as register_error_handlers
from .airports import airports_blueprint
from .airspace import airspace_blueprint
from .mapitems import mapitems_blueprint
from .waves import waves_blueprint
from .json import jsonify


def register(app):
    """
    :param flask.Flask app: a Flask app
    """

    @app.before_request
    def require_user_agent():
        """
        API requests require a ``User-Agent`` header
        """
        user_agent = request.user_agent
        assert isinstance(user_agent, UserAgent)

        if not user_agent.string:
            return jsonify({
                'message': 'You don\'t have the permission to access the API with a User-Agent header.',
            }, status=403)

    register_error_handlers(app)

    app.register_blueprint(airports_blueprint, url_prefix='/airports')
    app.register_blueprint(airspace_blueprint, url_prefix='/airspace')
    app.register_blueprint(mapitems_blueprint, url_prefix='/mapitems')
    app.register_blueprint(waves_blueprint, url_prefix='/mountain_wave_project')
