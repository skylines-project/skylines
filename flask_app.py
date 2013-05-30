#!/usr/bin/env python

# Flask app
from skylines import app

if __name__ == '__main__':
    # Run the WSGI server
    app.add_web_components()
    app.run(port=8080)
