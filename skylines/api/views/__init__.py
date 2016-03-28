from flask import request
from webargs import fields
from werkzeug.exceptions import Forbidden
from werkzeug.useragents import UserAgent

from skylines.api.cors import cors
from skylines.api.oauth import oauth


def register(app):
    """
    :param flask.Flask app: a Flask app
    """

    from .errors import register as register_error_handlers
    from .airports import airports_blueprint
    from .airspace import airspace_blueprint
    from .clubs import clubs_blueprint
    from .mapitems import mapitems_blueprint
    from .search import search_blueprint
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

    cors.init_app(app)
    oauth.init_app(app)

    register_error_handlers(app)

    app.register_blueprint(airports_blueprint)
    app.register_blueprint(airspace_blueprint)
    app.register_blueprint(clubs_blueprint)
    app.register_blueprint(mapitems_blueprint)
    app.register_blueprint(search_blueprint)
    app.register_blueprint(user)
    app.register_blueprint(users)
    app.register_blueprint(waves_blueprint)


pagination_args = {
    'page': fields.Integer(missing=1, location='query', validate=lambda val: val > 0),
    'per_page': fields.Integer(missing=30, location='query', validate=lambda val: val <= 100),
}
