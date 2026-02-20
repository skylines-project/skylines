# -*- coding: utf-8 -*-
#
# Docker container configuration.
# Reads connection strings and paths from environment variables
# so docker-compose can inject them.

import os

DEBUG = os.getenv("SKYLINES_DEBUG", "").lower() in ("1", "true", "yes")
SECRET_KEY = os.getenv("SECRET_KEY", "skylines-docker")

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db/skylines"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")

BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERYD_LOG_LEVEL = os.getenv("CELERYD_LOG_LEVEL", "INFO")

SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
EMAIL_FROM = os.getenv("EMAIL_FROM", "SkyLines <no-reply@skylines.aero>")

_base = "/home/skylines/code"

ASSETS_LOAD_DIR = os.path.join(_base, "skylines", "frontend", "static")
SKYLINES_FILES_PATH = os.getenv(
    "SKYLINES_FILES_PATH", os.path.join(_base, "htdocs", "files")
)
SKYLINES_ELEVATION_PATH = os.getenv(
    "SKYLINES_ELEVATION_PATH", os.path.join(_base, "htdocs", "srtm")
)
SKYLINES_MAPSERVER_PATH = os.path.join(_base, "mapserver")

SKYLINES_TEMPORARY_DIR = "/tmp"
SKYLINES_LISTS_DISPLAY_LENGTH = 50

SKYLINES_MAP_TILE_URL = os.getenv(
    "SKYLINES_MAP_TILE_URL", "http://caddy/mapproxy"
)

SKYLINES_ANALYSIS_ITER = 10e6
SKYLINES_ANALYSIS_MEMORY = 256

SKYLINES_AIRSPACE_CHECK = (
    "RESTRICT",
    "DANGER",
    "PROHIBITED",
    "CTR",
    "CLASSA",
    "CLASSB",
    "CLASSC",
    "CLASSD",
    "NOGLIDER",
    "TMZ",
    "MATZ",
)
