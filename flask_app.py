#!/usr/bin/env python

# Flask app
from skylines import app as flask_app

# ToscaWidgets
from tw.api import make_middleware

# TurboGears app
from skylines.config import environment as tg_env

# WSGI server
from werkzeug.serving import run_simple
from paste.cascade import Cascade


if __name__ == '__main__':
    # Insert ToscaWidgets Middleware
    flask_app.wsgi_app = make_middleware(flask_app.wsgi_app, stack_registry=True)

    # Create TurboGears app
    tg_env.load_from_file()

    # Create WSGI cascade with tg priority
    app = Cascade([flask_app])

    # Run the WSGI server
    run_simple('localhost', 5000, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
