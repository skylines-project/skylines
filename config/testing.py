# -*- coding: utf-8 -*-

from tempfile import mkdtemp

TESTING = True

SQLALCHEMY_DATABASE_URI = "postgresql:///skylines_test"
SQLALCHEMY_ECHO = False
SKYLINES_FILES_PATH = mkdtemp(suffix="skylines-uploads")
