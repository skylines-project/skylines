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

        self.add_sqlalchemy()

    def add_sqlalchemy(self):
        """ Create and configure SQLAlchemy extension """
        from skylines.model import db
        db.init_app(self)

    def add_web_components(self):
        self.add_logging_handlers()
        self.add_debug_toolbar()

        self.configure_jinja()
        self.add_cache()
        self.add_babel()
        self.add_login_manager()
        self.add_assets()
        self.add_tg2_compat()
        self.add_celery()

        self.add_mapproxy()

        self.register_views()

    def add_cache(self):
        """ Create and attach Cache extension """
        from flask.ext.cache import Cache
        self.cache = Cache(self)

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

    def register_views(self):
        import skylines.views
        skylines.views.register(self)

    def add_mapproxy(self):
        mapproxy_config = self.config.get('SKYLINES_MAPPROXY')
        if not mapproxy_config:
            return

        from werkzeug.wsgi import DispatcherMiddleware
        import mapproxy.wsgiapp as mapproxy

        self.wsgi_app = DispatcherMiddleware(self.wsgi_app, {
            '/mapproxy': mapproxy.make_wsgi_app(mapproxy_config),
        })

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
    return SkyLines(config_file)


def create_frontend_app(config_file=None):
    app = create_app(config_file)
    app.add_web_components()
    return app


def create_celery_app(config_file=None):
    app = create_app(config_file)
    return app.add_celery()
