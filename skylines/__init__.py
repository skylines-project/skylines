from flask import Flask, g, request, session
from flask.ext.babel import Babel, get_locale
from babel import Locale
from flask.ext.assets import Environment
from flask.ext.login import LoginManager, current_user
from webassets.loaders import PythonLoader
from skylines.lib import helpers
from .model import User


def create_app():
    app = Flask(__name__, static_folder='public')
    app.config.from_object('skylines.config.default')

    babel = Babel(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    bundles = PythonLoader('skylines.assets.bundles').load_bundles()
    assets = Environment(app)

    load_path = app.config.get('ASSETS_LOAD_DIR', None)
    if load_path is not None:
        load_url = app.config.get('ASSETS_LOAD_URL', None)
        assets.append_path(load_path, load_url)

    assets.register(bundles)

    return app

app = create_app()
babel = app.babel_instance

import skylines.views

@app.login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@app.before_request
def inject_request_identity():
    if current_user.is_anonymous():
        request.identity = None
    else:
        request.identity = {'user': current_user}


@app.before_request
def inject_active_locale():
    g.available_locales = app.babel_instance.list_translations()
    g.active_locale = get_locale()


@babel.localeselector
def select_locale():
    available = map(str, g.available_locales)
    preferred = []

    session_language = session.get('language', None)
    print 'session lang: {}'.format(session_language)
    if session_language:
        preferred.append(session_language)

    preferred.extend([l[0] for l in request.accept_languages])

    best_match = Locale.negotiate(preferred, available)
    if best_match:
        return str(best_match)


@app.context_processor
def inject_helpers_lib():
    return dict(h=helpers)

@app.context_processor
def inject_template_context():
    return dict(c=g)
