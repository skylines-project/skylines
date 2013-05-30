from flask import Flask, g, request
from flask.ext.babel import Babel
from skylines.assets import Environment
from flask.ext.login import LoginManager, current_user
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from skylines.lib import helpers


class SkyLines(Flask):
    def __init__(self):
        # Create Flask instance
        super(SkyLines, self).__init__(__name__, static_folder='public')

        # Load default settings and from environment variable
        self.config.from_object('skylines.config.default')
        self.config.from_envvar('SKYLINES_CONFIG', silent=True)

        # Configure Jinja2 template engine
        self.jinja_options['extensions'].append('jinja2.ext.do')

        self.add_sqlalchemy()
        self.add_cache()
        self.add_babel()
        self.add_login_manager()
        self.add_assets()
        self.add_toscawidgets()
        self.add_tg2_compat()

    def add_sqlalchemy(self):
        # Create and configure SQLAlchemy extension
        self.db = SQLAlchemy(self, session_options=dict(expire_on_commit=False))

    def add_cache(self):
        # Create and attach Cache extension
        self.cache = Cache(self)

    def add_babel(self):
        # Create and attach Babel extension
        self.babel = Babel(self)

    def add_login_manager(self):
        # Create and attach Login extension
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)

    def add_assets(self):
        # Create and attach Assets extension
        self.assets = Environment(self)
        self.assets.load_bundles('skylines.assets.bundles')

    def add_toscawidgets(self):
        from tw.api import make_middleware
        self.wsgi_app = make_middleware(self.wsgi_app, stack_registry=True)

    def add_tg2_compat(self):
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

        @self.context_processor
        def inject_template_context():
            g.identity = request.identity
            return dict(c=g, tmpl_context=g)

    def register_views(self):
        import skylines.views
        skylines.views.register(self)


app = SkyLines()
app.register_views()
