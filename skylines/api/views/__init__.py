from .errors import register as register_error_handlers
from .api import api_blueprint


def register(app):
    register_error_handlers(app)

    app.register_blueprint(api_blueprint)
