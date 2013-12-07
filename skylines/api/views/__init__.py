from .errors import register as register_error_handlers
from .airports import airports_blueprint
from .airspace import airspace_blueprint
from .mapitems import mapitems_blueprint
from .waves import waves_blueprint


def register(app):
    register_error_handlers(app)

    app.register_blueprint(airports_blueprint, url_prefix='/airports')
    app.register_blueprint(airspace_blueprint, url_prefix='/airspace')
    app.register_blueprint(mapitems_blueprint, url_prefix='/mapitems')
    app.register_blueprint(waves_blueprint, url_prefix='/mountain_wave_project')
