#!/usr/bin/env python

# Flask app
from skylines import app

# ToscaWidgets
from tw.api import make_middleware

# TurboGears app
from skylines.config import environment as tg_env

# WSGI server
from werkzeug.serving import run_simple


if __name__ == '__main__':
    # Insert ToscaWidgets Middleware
    app.wsgi_app = make_middleware(app.wsgi_app, stack_registry=True)

    # Create TurboGears app
    tg_env.load_from_file()

    # Run the WSGI server
    run_simple('localhost', 8080, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
