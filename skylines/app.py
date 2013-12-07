import os
import config

from flask import Flask


class SkyLines(Flask):
    def __init__(self, config_file=None):
        # Create Flask instance
        super(SkyLines, self).__init__(__name__)

        # Load default settings and from environment variable
        self.config.from_pyfile(config.DEFAULT_CONF_PATH)

        if 'SKYLINES_CONFIG' in os.environ:
            self.config.from_pyfile(os.environ['SKYLINES_CONFIG'])

        if config_file:
            self.config.from_pyfile(config_file)

    def add_sqlalchemy(self):
        """ Create and configure SQLAlchemy extension """
        from skylines.model import db
        db.init_app(self)

    def add_cache(self):
        """ Create and attach Cache extension """
        from flask.ext.cache import Cache
        self.cache = Cache(self, with_jinja2_ext=False)

    def add_babel(self):
        """ Create and attach Babel extension """
        from flask.ext.babel import Babel
        self.babel = Babel(self)

    def add_login_manager(self):
        """ Create and attach Login extension """
        from flask.ext.login import LoginManager
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)

    def add_assets(self):
        """ Create and attach Assets extension """
        from skylines.assets import Environment
        self.assets = Environment(self)
        self.assets.load_bundles('skylines.assets.bundles')

    def add_tg2_compat(self):
        from skylines.lib import helpers

        @self.context_processor
        def inject_helpers_lib():
            return dict(h=helpers)

    def configure_jinja(self):
        from itertools import izip

        # Configure Jinja2 template engine
        self.jinja_options['extensions'].append('jinja2.ext.do')

        @self.template_filter('add_to_dict')
        def add_to_dict(d, **kw):
            return dict(d, **kw)

        @self.template_global()
        def zip(*args, **kw):
            return izip(*args, **kw)

    def add_logging_handlers(self):
        import logging
        from logging import handlers

        self.logger.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

        for level, klass, args in self.config.get('LOGGING_HANDLERS', []):
            handler = getattr(handlers, klass)(*args)
            handler.setLevel(getattr(logging, level))
            if 'FileHandler' in klass:
                handler.setFormatter(file_formatter)

            self.logger.addHandler(handler)

    def add_debug_toolbar(self):
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(self)

    def add_celery(self):
        from skylines.worker.celery import celery
        celery.init_app(self)
        return celery


def create_app(config_file=None):
    app = SkyLines(config_file)
    app.add_sqlalchemy()
    return app


def create_http_app(config_file=None):
    app = create_app(config_file)

    app.add_logging_handlers()
    app.add_cache()
    app.add_celery()

    return app


def create_frontend_app(config_file=None):
    app = create_http_app(config_file)

    app.add_debug_toolbar()

    app.configure_jinja()
    app.add_babel()
    app.add_login_manager()
    app.add_assets()
    app.add_tg2_compat()

    import skylines.frontend.views
    skylines.frontend.views.register(app)

    return app


def create_api_app(config_file=None):
    app = create_http_app(config_file)

    import skylines.api.views
    skylines.api.views.register(app)

    return app


def create_combined_app(config_file=None):
    from werkzeug.wsgi import DispatcherMiddleware

    frontend = create_frontend_app(config_file)
    api = create_api_app(config_file)

    mounts = {
        '/api': api,
    }

    if frontend.config.get('SKYLINES_MAPPROXY'):
        from mapproxy.wsgiapp import make_wsgi_app as create_mapproxy_app

        mapproxy = create_mapproxy_app(
            frontend.config.get('SKYLINES_MAPPROXY'))

        mounts['/mapproxy'] = mapproxy

    frontend.wsgi_app = DispatcherMiddleware(frontend.wsgi_app, mounts)
    return frontend


def create_celery_app(config_file=None):
    app = create_app(config_file)
    return app.add_celery()
