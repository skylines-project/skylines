#!/usr/bin/env python

# Flask app
from skylines import app

# WSGI server
from werkzeug.serving import run_simple


if __name__ == '__main__':
    # Run the WSGI server
    run_simple('localhost', 8080, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
