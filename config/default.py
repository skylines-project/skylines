# -*- coding: utf-8 -*-

import os.path

here = os.path.abspath(os.path.dirname(__file__))
base = os.path.abspath(os.path.join(here, '..'))

# Enables the wdb debugger (you need the flask-wdb package for this)
#WDB_ENABLED = True

DEBUG_TB_INTERCEPT_REDIRECTS = False

DEBUG = True
SECRET_KEY = 'skylines'

SMTP_SERVER = 'localhost'
EMAIL_FROM = 'no-reply@skylines-project.org'

"""
# Logging handlers (disabled in DEBUG mode)

ADMINS = [
    'tobias.bieniek@gmx.de'
]

mail_handler = (
    'ERROR', 'SMTPHandler',
    ('localhost', 'error@skylines-project.org', ADMINS, 'SkyLines Error Report'))

file_handler = (
    'INFO', 'RotatingFileHandler',
    ('/home/turbo/skylines.log', 'a', 10000, 4))

LOGGING_HANDLERS = [mail_handler, file_handler]
"""

# This should probably be changed for a multi-threaded production server
CACHE_TYPE = 'simple'

SQLALCHEMY_DATABASE_URI = 'postgresql:///skylines'

ASSETS_DEBUG = False
ASSETS_AUTO_BUILD = True
ASSETS_DIRECTORY = os.path.join(base, 'webassets')
ASSETS_URL = '/assets'
ASSETS_LOAD_DIR = os.path.join(base, 'skylines', 'assets', 'static')
ASSETS_LOAD_URL = '/'

SKYLINES_FILES_PATH = os.path.join(base, 'htdocs', 'files')
SKYLINES_ELEVATION_PATH = os.path.join(base, 'htdocs', 'srtm')

SKYLINES_TEMPORARY_DIR = '/tmp'

# how many entries should a list have?
SKYLINES_LISTS_DISPLAY_LENGTH = 50

# switch to server-side processing for lists with more than ... entries
# this shall not be smaller than the display_lenght setting
SKYLINES_LISTS_SERVER_SIDE = 250

# mapproxy config file; if commented,
# SKYLINES_MAP_TILE_URL is used instead
#SKYLINES_MAPPROXY = os.path.join(base, 'mapserver', 'mapproxy', 'mapproxy.yaml')

SKYLINES_MAP_TILE_URL = 'https://www.skylines-project.org'

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERYD_LOG_LEVEL = 'INFO'

# subprocess limits for AnalyseFlight
# see RLIMIT_CPU and RLIMIT_AS at http://linux.die.net/man/2/setrlimit
SKYLINES_SUBPROCESS_CPU = 120 # soft limit in seconds (hard limit: * 1.2)
SKYLINES_SUBPROCESS_MEMORY = 256 # MB, soft limit (hard limit: * 1.2)
