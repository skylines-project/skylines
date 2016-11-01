from .errors import register as register_error_handlers

from .assets import assets_blueprint
from .files import files_blueprint
from .livetrack24 import lt24_blueprint
from .widgets import widgets_blueprint


def register(app):
    register_error_handlers(app)

    app.register_blueprint(assets_blueprint)
    app.register_blueprint(files_blueprint)
    app.register_blueprint(lt24_blueprint)
    app.register_blueprint(widgets_blueprint)
