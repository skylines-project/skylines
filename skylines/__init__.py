from flask import Flask, g, request
from flask.ext.babel import Babel
from skylines.assets import Environment
from flask.ext.login import LoginManager, current_user
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from skylines.lib import helpers


class SkyLines(Flask):
    def __init__(self):
        super(SkyLines, self).__init__(__name__, static_folder='public')
        self.config.from_object('skylines.config.default')
        self.config.from_envvar('SKYLINES_CONFIG', silent=True)

        self.jinja_options['extensions'].append('jinja2.ext.do')

        self.cache = Cache(self)
        self.db = SQLAlchemy(self, session_options=dict(expire_on_commit=False))

        babel = Babel(self)
        login_manager = LoginManager()
        login_manager.init_app(self)

        assets = Environment(self)
        assets.load_bundles('skylines.assets.bundles')

    def inject_tg2_compat(self):
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
app.inject_tg2_compat()
app.register_views()
