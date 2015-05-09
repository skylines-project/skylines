from flask import request
from webargs import Arg
from werkzeug.exceptions import Forbidden
from werkzeug.useragents import UserAgent

from skylines.api import auth


def register(app):
    """
    :param flask.Flask app: a Flask app
    """

    from .errors import register as register_error_handlers
    from .airports import airports_blueprint
    from .airspace import airspace_blueprint
    from .mapitems import mapitems_blueprint
    from .users import users
    from .user import user
    from .waves import waves_blueprint

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

    app.before_request(auth.check)

    @app.after_request
    def add_cors_headers(response):
        if 'Origin' in request.headers:
            response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
            response.headers.add('Access-Control-Allow-Credentials', 'true')

            if 'Access-Control-Request-Methods' in request.headers:
                response.headers.add('Access-Control-Allow-Methods', request.headers.get('Access-Control-Request-Methods'))

            if 'Access-Control-Request-Headers' in request.headers:
                response.headers.add('Access-Control-Allow-Headers', request.headers.get('Access-Control-Request-Headers'))

        return response

    register_error_handlers(app)

    app.register_blueprint(airports_blueprint)
    app.register_blueprint(airspace_blueprint)
    app.register_blueprint(mapitems_blueprint)
    app.register_blueprint(waves_blueprint)
    app.register_blueprint(user)
    app.register_blueprint(users)


pagination_args = {
    'page': Arg(
        int, default=1, location='query',
        validate=lambda val: val > 0, error='Invalid "page" parameter'),

    'per_page': Arg(
        int, default=30, location='query',
        validate=lambda val: val <= 100, error='Invalid "per_page" parameter'),
}
