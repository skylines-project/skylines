import os.path

DEFAULT_CONF_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'config', 'default.py'))


from flask import Flask


class SkyLines(Flask):
    def __init__(self):
        # Create Flask instance
        super(SkyLines, self).__init__(__name__, static_folder='public')

        # Load default settings and from environment variable
        self.config.from_pyfile(DEFAULT_CONF_PATH)
        self.config.from_envvar('SKYLINES_CONFIG', silent=True)

        # Configure Jinja2 template engine
        self.jinja_options['extensions'].append('jinja2.ext.do')

        self.add_sqlalchemy()

    def add_sqlalchemy(self):
        """ Create and configure SQLAlchemy extension """
        from flask.ext.sqlalchemy import SQLAlchemy
        self.db = SQLAlchemy(self, session_options=dict(expire_on_commit=False))

    def add_web_components(self):
        self.add_cache()
        self.add_babel()
        self.add_login_manager()
        self.add_assets()
        self.add_toscawidgets()
        self.add_tg2_compat()

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
        from flask import request
        from flask.ext.login import current_user
        from skylines.lib import helpers

        @self.before_request
        def inject_request_identity():
            """ for compatibility with tg2 """

            if not hasattr(request, 'identity'):
                request.identity = {}

            if not current_user.is_anonymous():
                request.identity['user'] = current_user

                request.identity['groups'] = \
                    [g.group_name for g in current_user.groups]

                request.identity['permissions'] = \
                    [p.permission_name for p in current_user.permissions]

        @self.context_processor
        def inject_helpers_lib():
            return dict(h=helpers)

    def register_views(self):
        import skylines.views
        skylines.views.register(self)


app = SkyLines()
db = app.db
