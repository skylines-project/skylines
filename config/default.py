# -*- coding: utf-8 -*-

import os.path

here = os.path.abspath(os.path.dirname(__file__))
base = os.path.abspath(os.path.join(here, '..'))

DEBUG_TB_INTERCEPT_REDIRECTS = False

DEBUG = True
SECRET_KEY = 'skylines'

SMTP_SERVER = 'localhost'
EMAIL_FROM = 'no-reply@skylines.aero'

"""
# Logging handlers (disabled in DEBUG mode)

ADMINS = [
    'tobias.bieniek@gmx.de'
]

mail_handler = (
    'ERROR', 'SMTPHandler',
    ('localhost', 'error@skylines.aero', ADMINS, 'SkyLines Error Report'))

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
ASSETS_LOAD_DIR = os.path.join(base, 'skylines', 'frontend', 'static')
ASSETS_LOAD_URL = '/'

SKYLINES_FILES_PATH = os.path.join(base, 'htdocs', 'files')
SKYLINES_ELEVATION_PATH = os.path.join(base, 'htdocs', 'srtm')
SKYLINES_MAPSERVER_PATH = os.path.join(base, 'mapserver')
SKYLINES_BACKEND_PATH = os.path.join(base, 'backend')

SKYLINES_TEMPORARY_DIR = '/tmp'

# how many entries should a list have?
SKYLINES_LISTS_DISPLAY_LENGTH = 50

SKYLINES_API_URL = 'http://localhost:5001'
SKYLINES_MAP_TILE_URL = 'https://www.skylines.aero/mapproxy'

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERYD_LOG_LEVEL = 'INFO'

# limits for AnalyseFlight
SKYLINES_ANALYSIS_ITER = 10e6 # iteration limit, should be around 10e6 to 50e6
SKYLINES_ANALYSIS_MEMORY = 256 # approx memory limit in MB

# List of airspace types to check for infringements
SKYLINES_AIRSPACE_CHECK = ('RESTRICT', 'DANGER', 'PROHIBITED', 'CTR',
                           'CLASSA', 'CLASSB', 'CLASSC', 'CLASSD',
                           'NOGLIDER', 'TMZ', 'MATZ')

SKYLINES_CESIUM_PATH = os.path.join(base, 'skylines', 'frontend', 'static', 'vendor', 'openlayers', 'cesium')
