import os
import config

from flask import Flask, request, g

from skylines.api.middleware import HTTPMethodOverrideMiddleware


class SkyLines(Flask):
    def __init__(self, name='skylines', config_file=None, *args, **kw):
        # Create Flask instance
        super(SkyLines, self).__init__(name, *args, **kw)

        # Load default settings and from environment variable
        self.config.from_pyfile(config.DEFAULT_CONF_PATH)

        if 'SKYLINES_CONFIG' in os.environ:
            self.config.from_pyfile(os.environ['SKYLINES_CONFIG'])

        if config_file:
            self.config.from_pyfile(config_file)

    def add_sqlalchemy(self):
        """ Create and configure SQLAlchemy extension """
        from skylines.database import db, migrate
        db.init_app(self)
        migrate.init_app(self, db)

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
        from skylines.frontend.assets import Environment
        self.assets = Environment(self)
        self.assets.load_bundles('skylines.frontend.assets.bundles')

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
        if self.debug: return

        import logging
        from logging import Formatter, Filter
        from logging.handlers import RotatingFileHandler, SMTPHandler

        # Set general log level
        self.logger.setLevel(logging.INFO)

        # Inject additional log record fields
        class ContextFilter(Filter):
            def __init__(self, app):
                self.app = app

            def filter(self, record):
                record.app_name = self.app.name
                record.url = request.url
                record.ip = request.remote_addr
                if hasattr(g, 'current_user') and g.current_user:
                    user = g.current_user
                    record.user = '%s <%s>' % (user.name, user.email_address)
                else:
                    record.user = 'anonymous'

                def filter_password(k, v):
                    if 'password' in k:
                        v = 'xxxxxxx'

                    return (k, v)

                record.request_args = '\n'.join('%s: %r' % (k, v) for (k, v) in request.args.iteritems())
                record.request_form = '\n'.join('%s: %r' % filter_password(k, v) for (k, v) in request.form.iteritems())

                return True

        self.logger.addFilter(ContextFilter(self))

        # Add SMTP handler
        mail_handler = SMTPHandler(
            'localhost', 'error@skylines.aero',
            self.config.get('ADMINS', []), 'SkyLines Error Report')
        mail_handler.setLevel(logging.ERROR)

        mail_formatter = Formatter('''
App:                %(app_name)s
Time:               %(asctime)s
URL:                %(url)s
IP:                 %(ip)s
User:               %(user)s

Args:
%(request_args)s

Form:
%(request_form)s

Message:

%(message)s
''')
        mail_handler.setFormatter(mail_formatter)
        self.logger.addHandler(mail_handler)

        # Add log file handler (if configured)
        path = self.config.get('LOGFILE')
        if path:
            file_handler = RotatingFileHandler(path, 'a', 10000, 4)
            file_handler.setLevel(logging.INFO)

            file_formatter = Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
            file_handler.setFormatter(file_formatter)

            self.logger.addHandler(file_handler)

    def add_debug_toolbar(self):
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(self)
        except ImportError:
            pass

    def add_celery(self):
        from skylines.worker.celery import celery
        celery.init_app(self)
        return celery

    def initialize_lib(self):
        from skylines.lib.geoid import load_geoid
        load_geoid(self)


def create_app(*args, **kw):
    app = SkyLines(*args, **kw)
    app.add_sqlalchemy()
    app.add_cache()
    app.initialize_lib()
    return app


def create_http_app(*args, **kw):
    app = create_app(*args, **kw)

    app.add_logging_handlers()
    app.add_celery()

    return app


def create_frontend_app(*args, **kw):
    app = create_http_app('skylines.frontend', *args, **kw)

    app.add_debug_toolbar()

    app.configure_jinja()
    app.add_babel()
    app.add_login_manager()
    app.add_assets()
    app.add_tg2_compat()

    import skylines.frontend.views
    skylines.frontend.views.register(app)

    return app


def create_api_app(*args, **kw):
    app = create_http_app('skylines.api', *args, **kw)
    app.config['JSON_SORT_KEYS'] = False

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    import skylines.api.views
    skylines.api.views.register(app)

    return app


def create_combined_app(*args, **kw):
    from werkzeug.wsgi import DispatcherMiddleware

    frontend = create_frontend_app(*args, **kw)
    api = create_api_app(*args, **kw)

    mounts = {
        '/api': api,
    }

    frontend.wsgi_app = DispatcherMiddleware(frontend.wsgi_app, mounts)
    return frontend


def create_celery_app(*args, **kw):
    app = create_app('skylines.worker', *args, **kw)
    app.add_celery()
    return app
