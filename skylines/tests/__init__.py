# -*- coding: utf-8 -*-
"""Unit and functional test suite for SkyLines."""

from os import path
import sys

from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from routes import url_for
from webtest import TestApp
from nose.tools import eq_

from skylines import model

__all__ = ['setup_db', 'teardown_db', 'TestController', 'url_for']


def setup_db():
    """Method used to build a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.init_model(engine)
    model.metadata.create_all(engine)


def teardown_db():
    """Method used to destroy a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)


class TestController(object):
    """
    Base functional test case for the controllers.
    """

    application_under_test = 'main'

    def setUp(self):
        """Method called by nose before running each test"""
        # Loading the application:
        conf_dir = config.here
        wsgiapp = loadapp('config:test.ini#%s' % self.application_under_test,
                          relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        # Setting it up:
        test_file = path.join(conf_dir, 'test.ini')
        cmd = SetupCommand('setup-app')
        cmd.run([test_file])

    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        model.DBSession.remove()
        teardown_db()
