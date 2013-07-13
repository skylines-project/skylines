import os
import config

from flask import Flask


class SkyLines(Flask):
    def __init__(self):
        # Create Flask instance
        super(SkyLines, self).__init__(__name__, static_folder='public')

        # Load default settings and from environment variable
        self.config.from_pyfile(config.DEFAULT_CONF_PATH)

        if self.created_by_nose:
            self.config.from_pyfile(config.TESTING_CONF_PATH)

        if 'SKYLINES_CONFIG' in os.environ:
            self.config.from_pyfile(os.environ['SKYLINES_CONFIG'])

        self.add_wdb()
        self.add_sqlalchemy()
        self.add_celery()

    @property
    def created_by_nose(self):
        import traceback
        stack = traceback.extract_stack()
        top_frame = stack[0]
        filename = os.path.abspath(top_frame[0])

        # Started by calling "nosetests"
        if filename.endswith('nosetests'):
            return True

        # Started by calling unit test file (e.g. ./test_pep8.py)
        if os.path.join('skylines', 'tests') in filename:
            return True

        # Started by calling "python setup.py test/nosetests"
        if filename.endswith('setup.py'):
            cmd_frame = stack[4]
            filename = os.path.abspath(cmd_frame[0])

            if filename.endswith('test.py'):
                return True

            if filename.endswith('nose/commands.py'):
                return True

        return False

    def add_sqlalchemy(self):
        """ Create and configure SQLAlchemy extension """
        from flask.ext.sqlalchemy import SQLAlchemy
        self.db = SQLAlchemy(self, session_options=dict(expire_on_commit=False))

    def add_web_components(self):
        self.add_logging_handlers()
        self.add_debug_toolbar()

        self.configure_jinja()
        self.add_cache()
        self.add_babel()
        self.add_login_manager()
        self.add_assets()
        self.add_toscawidgets()
        self.add_tg2_compat()

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

    def add_toscawidgets(self):
        from tw.api import make_middleware
        self.wsgi_app = make_middleware(self.wsgi_app, stack_registry=True)

    def add_tg2_compat(self):
        from skylines.lib import helpers

        @self.context_processor
        def inject_helpers_lib():
            return dict(h=helpers)

    def configure_jinja(self):
        # Configure Jinja2 template engine
        self.jinja_options['extensions'].append('jinja2.ext.do')

        @self.template_filter('add_to_dict')
        def add_to_dict(d, **kw):
            return dict(d, **kw)

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

    def add_wdb(self):
        if self.config.get('WDB_ENABLED', False):
            from flask_wdb import Wdb
            Wdb(self)

    def add_celery(self):
        from skylines.worker.celery import make_celery
        self.celery = make_celery(self)


app = SkyLines()
db = app.db
celery = app.celery
