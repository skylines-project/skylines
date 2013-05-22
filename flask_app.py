#!/usr/bin/env python

# Flask app
from skylines import app as flask_app

# TurboGears app
from skylines.config.middleware import make_app
from skylines.config.environment import conf_from_file

# WSGI server
from werkzeug.serving import run_simple
from paste.cascade import Cascade


if __name__ == '__main__':
    flask_app.debug = True

    # Create TurboGears app
    tg_conf = conf_from_file()
    tg_app = make_app(tg_conf.global_conf, **tg_conf.local_conf)

    # Create WSGI cascade with flask priority
    app = Cascade([flask_app, tg_app])

    # Run the WSGI server
    run_simple('localhost', 5000, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
