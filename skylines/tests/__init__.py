# -*- coding: utf-8 -*-
"""Unit and functional test suite for SkyLines."""

from os import path

from tg import config
from paste.script.appinstall import SetupCommand
from routes import url_for

from skylines import model

__all__ = ['setup_db', 'setup_app', 'teardown_db', 'url_for']


def setup_db():
    """Method used to build a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.init_model(engine)
    model.metadata.create_all(engine)


def setup_app():
    test_file = path.join(config.here, 'test.ini')
    cmd = SetupCommand('setup-app')
    cmd.run([test_file])


def teardown_db():
    """Method used to destroy a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)
